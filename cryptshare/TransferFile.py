import hashlib
import logging
import os
import typing

import requests

from cryptshare.ApiRequestHandler import ApiRequestHandler
from cryptshare.Header import Header

logger = logging.getLogger(__name__)


class TransferFile(ApiRequestHandler):
    def __init__(self, path: str, header: Header, ssl_verify: bool):
        logger.debug(f"Initialising Cryptshare TransferFile object for file: {path}")
        self.size = os.stat(path).st_size
        self.name = os.path.basename(path)
        self.path = path
        self.header = header
        self.ssl_verify = ssl_verify
        # Calculate file hashsum
        with open(self.path, "rb") as data:
            file_content = data.read()
            self.checksum = hashlib.sha256(file_content).hexdigest()

    location = ""

    def set_location(self, location):
        logger.debug(f"Setting location to {location}")
        self.location = location

    def data(self):
        logger.debug("Returning TransferFile data")
        return {"fileName": self.name, "size": self.size, "checksum": self.checksum}

    def read_file_contents(self) -> typing.AnyStr:
        logger.debug(f"Reading file contents from {self.path}")
        try:
            return open(self.path, "rb").read()
        except FileNotFoundError:
            logger.error(f"File {self.path} not found")
            return ""
        except Exception as e:
            logger.error(f"Error reading file {self.path}: {e}")
            return ""

    def upload(self):
        logger.debug(f"Uploading file {self.name} to {self.location}")
        data = open(self.path, "rb").read()
        self._handle_response(
            requests.put(
                self.location + "/content",
                data=data,
                verify=self.ssl_verify,
                headers=self.header,
            )
        )
        return True

    def delete_upload(self):
        logger.debug(f"Deleting uploaded file {self.name} from {self.location}")
        self._handle_response(requests.delete(self.location, verify=self.ssl_verify, headers=self.header))
        return True
