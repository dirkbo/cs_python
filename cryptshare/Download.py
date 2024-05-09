import requests
import logging

from cryptshare.ApiRequestHandler import ApiRequestHandler

logger = logging.getLogger(__name__)


class Download(ApiRequestHandler):
    def __init__(self, url, header, transfer_id, password, ssl_verify=True):
        logger.debug(f"Initialising Cryptshare Download for transfer: {transfer_id}")
        self.url = url
        self.ssl_verify = ssl_verify
        self.header = header
        self.transfer_id = transfer_id
        self.password = password

    def download_transfer_information(self):
        logger.debug(f"Downloading transfer information for transfer: {self.transfer_id}")
        r = self._handle_response(
            requests.get(
                self.url + "/transfers/" + self.transfer_id + "?password=" + self.password,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def download_zip(self):
        logger.debug(f"Downloading zip for transfer: {self.transfer_id}")
        r = self._handle_response(
            requests.get(
                self.url + "/transfers/" + self.transfer_id + "/zip?password=" + self.password,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def download_eml(self):
        logger.debug(f"Downloading eml for transfer: {self.transfer_id}")
        r = self._handle_response(
            requests.get(
                self.url + "/transfers/" + self.transfer_id + "/eml?password=" + self.password,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def download_files_info(self):
        logger.debug(f"Downloading files info for transfer: {self.transfer_id}")
        r = self._handle_response(
            requests.get(
                self.url + "/transfers/" + self.transfer_id + "/files?password=" + self.password,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r
