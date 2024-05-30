import logging
import os

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

    def download_zip_info(self):
        path = f"{self.server}/api/transfers/{self.transfer_id}/zip?password={self.password}"
        logger.info(f"Downloading zip for transfer: {self.transfer_id} from {path}")
        return path

    def download_eml_info(self):
        path = f"{self.server}/api/transfers/{self.transfer_id}/eml?password={self.password}"
        logger.info(f"Downloading eml for transfer: {self.transfer_id} from {path}")
        r = self._request(
            "GET",
            path,
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.request_header,
        )
        return r

    def download_files_info(self):
        path = f"{self.server}/api/transfers/{self.transfer_id}/files?password={self.password}"
        logger.info(f"Downloading files info for transfer: {self.transfer_id} from {path}")
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

    def download_zip_file(self, directory):
        url = self.download_zip_info()
        print(f"url: {self.download_zip_info()}")
        self.download_file(url, f"{self.transfer_id}.zip", directory)

    def download_eml_file(self, directory):
        self.download_file(self.download_eml_info(), f"{self.transfer_id}.eml", directory)
