import logging
import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from cryptshare.api_requests import CryptshareApiRequests
from cryptshare.base_client import CryptshareBaseClient

logger = logging.getLogger(__name__)


class CryptshareDownload(CryptshareApiRequests):
    _cryptshare_client: CryptshareBaseClient = None

    def __init__(self, cryptshare_client: CryptshareBaseClient, transfer_id, password):
        logger.debug(f"Initialising Cryptshare Download for transfer: {transfer_id}")
        self._cryptshare_client = cryptshare_client
        self.transfer_id = transfer_id
        self.password = password

    @property
    def server(self):
        return self._cryptshare_client.server

    @staticmethod
    def _as_csv(values) -> [str, None]:
        if values is None:
            return None
        if isinstance(values, str):
            return values
        return ",".join(values)

    @staticmethod
    def _sanitize_url(url: str) -> str:
        parts = urlsplit(url)
        query = parse_qsl(parts.query, keep_blank_values=True)
        sanitized_query = [(key, "***" if key.lower() == "password" else value) for key, value in query]
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(sanitized_query), parts.fragment))

    def download_transfer_information(self):
        path = f"{self.server}/api/transfers/{self.transfer_id}?password={self.password}"
        logger.info(f"Downloading transfer information for transfer: {self.transfer_id} from {path}")
        r = self._request(
            "GET",
            path,
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.request_header,
        )
        return r

    def download_zip_info(self, include_file_ids=None, exclude_file_ids=None):
        params = {"password": self.password}
        included = self._as_csv(include_file_ids)
        excluded = self._as_csv(exclude_file_ids)
        if included:
            params["includedFileIds"] = included
        if excluded:
            params["excludedFileIds"] = excluded
        query = urlencode(params)
        path = f"{self.server}/api/transfers/{self.transfer_id}/zip?{query}"
        logger.info(f"Downloading zip for transfer: {self.transfer_id} from {self._sanitize_url(path)}")
        return path

    def download_eml_info(self):
        """Returns the URL to download the EML file of the transfer"""
        path = f"{self.server}/api/transfers/{self.transfer_id}/eml?password={self.password}"
        return path

    def download_files_info(self):
        path = f"{self.server}/api/transfers/{self.transfer_id}/files?password={self.password}"
        logger.info(f"Downloading files info for transfer: {self.transfer_id} from {self._sanitize_url(path)}")
        r = self._request(
            "GET",
            path,
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.request_header,
        )
        return r

    def download_file(self, url: str, filename: str, directory: str, size: int = None) -> None:
        """Download a file from an URL to the given directory"""
        response = self._request(
            "GET",
            url,
            stream=True,
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.request_header,
        )
        full_path = os.path.join(directory, filename)
        os.makedirs(directory, exist_ok=True)
        with open(full_path, "wb") as handle:
            for data in response.iter_content():
                handle.write(data)

    def download_transfer_file(self, file, directory: str) -> None:
        """Download a file of a Transfer to the given directory"""
        self.download_file(self.server + file["href"], file["fileName"], directory, size=file["size"])

    def download_all_files(self, directory: str) -> None:
        files_info = self.download_files_info()
        for file in files_info:
            self.download_transfer_file(file, directory)

    def download_zip_file(self, directory, include_file_ids=None, exclude_file_ids=None):
        files_info = self.download_files_info()
        url = self.download_zip_info(include_file_ids=include_file_ids, exclude_file_ids=exclude_file_ids)
        size = 0
        for file in files_info:
            size += file["size"]
        logger.info(f"url: {self._sanitize_url(url)} size: {size}")
        self.download_file(url, f"{self.transfer_id}.zip", directory, size=size)

    def download_eml_file(self, directory):
        files_info = self.download_files_info()
        size = 0
        for file in files_info:
            size += file["size"]
        path = self.download_eml_info()
        logger.info(f"Downloading eml for transfer: {self.transfer_id} from {self._sanitize_url(path)}")
        self.download_file(path, f"{self.transfer_id}.eml", directory, size=size)
