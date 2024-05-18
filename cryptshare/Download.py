import logging

import requests

from cryptshare.ApiRequestHandler import ApiRequestHandler

logger = logging.getLogger(__name__)


class Download(ApiRequestHandler):
    def __init__(self, server, header, transfer_id, password, ssl_verify=True):
        logger.debug(f"Initialising Cryptshare Download for transfer: {transfer_id}")
        self._server = server
        self.ssl_verify = ssl_verify
        self.header = header
        self.transfer_id = transfer_id
        self.password = password

    def download_transfer_information(self):
        path = f"{self._server}/api/transfers/{self.transfer_id}?password={self.password}"
        logger.info(f"Downloading transfer information for transfer: {self.transfer_id} from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def download_zip(self):
        path = f"{self._server}/api/transfers/{self.transfer_id}/zip?password={self.password}"
        logger.info(f"Downloading zip for transfer: {self.transfer_id} from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def download_eml(self):
        path = f"{self._server}/api/transfers/{self.transfer_id}/eml?password={self.password}"
        logger.info(f"Downloading eml for transfer: {self.transfer_id} from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def download_files_info(self):
        path = f"{self._server}/api/transfers/{self.transfer_id}/files?password={self.password}"
        logger.info(f"Downloading files info for transfer: {self.transfer_id} from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r
