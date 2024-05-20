import hashlib
import logging
import os
import typing

import requests

from cryptshare import CryptshareClient
from cryptshare.ApiRequestHandler import ApiRequestHandler
from cryptshare.CryptshareHeader import CryptshareHeader

logger = logging.getLogger(__name__)


class TransferFile(ApiRequestHandler):
    _location: str = ""

    def __init__(self, path: str):
        logger.debug(f"Initialising Cryptshare TransferFile object for file: {path}")
        self.size = os.stat(path).st_size
        self.name = os.path.basename(path)
        self.path = path
        # Calculate file hashsum
        with open(self.path, "rb") as data:
            file_content = data.read()
            self.checksum = hashlib.sha256(file_content).hexdigest()

    def set_location(self, location):
        logger.debug(f"Setting location to {location}")
        self._location = location

    def data(self):
        logger.debug("Returning TransferFile data")
        return {"fileName": self.name, "size": self.size, "checksum": self.checksum}

    def announce_upload(self, cryptshare_client: CryptshareClient, transfer_id: str):
        url = f"{self._location}/files"
        r = self._handle_response(
            requests.post(
                url,
                verify=cryptshare_client.ssl_verify,
                headers=cryptshare_client.header.request_header,
                json=self.data(),
            )
        )
        self.set_location(r)

    def upload(self, cryptshare_client: CryptshareClient):
        url = f"{self._location}/content"
        logger.info(f"Uploading file {self.name} content to {url}")
        data = open(self.path, "rb").read()
        self._handle_response(
            requests.put(
                url,
                data=data,
                verify=cryptshare_client.ssl_verify,
                headers=cryptshare_client.header.request_header,
            )
        )
        return True

    def delete_upload(self, cryptshare_client: CryptshareClient):
        logger.debug(f"Deleting uploaded file {self.name} from {self._location}")
        self._handle_response(
            requests.delete(
                self._location, verify=cryptshare_client.ssl_verify, headers=cryptshare_client.header.request_header
            )
        )
        return True
