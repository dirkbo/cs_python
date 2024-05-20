import logging
import os

import requests

from cryptshare import CryptshareClient
from cryptshare.ApiRequestHandler import ApiRequestHandler

logger = logging.getLogger(__name__)


class CryptshareDownload(ApiRequestHandler):
    _cryptshare_client: CryptshareClient = None

    def __init__(self, cryptshare_client: CryptshareClient, transfer_id, password):
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
        r = self._handle_response(
            requests.get(
                path,
                verify=self._cryptshare_client.ssl_verify,
                headers=self._cryptshare_client.header.request_header,
            )
        )
        return r

    def download_zip(self):
        path = f"{self.server}/api/transfers/{self.transfer_id}/zip?password={self.password}"
        logger.info(f"Downloading zip for transfer: {self.transfer_id} from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self._cryptshare_client.ssl_verify,
                headers=self._cryptshare_client.header.request_header,
            )
        )
        return r

    def download_eml(self):
        path = f"{self.server}/api/transfers/{self.transfer_id}/eml?password={self.password}"
        logger.info(f"Downloading eml for transfer: {self.transfer_id} from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self._cryptshare_client.ssl_verify,
                headers=self._cryptshare_client.header.request_header,
            )
        )
        return r

    def download_files_info(self):
        path = f"{self.server}/api/transfers/{self.transfer_id}/files?password={self.password}"
        logger.info(f"Downloading files info for transfer: {self.transfer_id} from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self._cryptshare_client.ssl_verify,
                headers=self._cryptshare_client.header.request_header,
            )
        )
        return r

    def download_file(self, file, directory):
        response = requests.get(self.server + file["href"], stream=True)
        full_path = os.path.join(directory, file["fileName"])
        os.makedirs(directory, exist_ok=True)
        with open(full_path, "wb") as handle:
            for data in response.iter_content():
                handle.write(data)

    def download_all_files(self, directory):
        files_info = self.download_files_info()
        for file in files_info:
            self.download_file(file, directory)
