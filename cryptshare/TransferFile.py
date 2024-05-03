import hashlib
import os
import typing

import requests

from cryptshare.ApiRequestHandler import ApiRequestHandler
from cryptshare.Header import Header


class TransferFile(ApiRequestHandler):
    def __init__(self, path: str, header: Header, ssl_verify: bool):
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
        self.location = location

    def data(self):
        return {"fileName": self.name, "size": self.size, "checksum": self.checksum}

    def read_file_contents(self) -> typing.AnyStr:
        return open(self.path, "rb").read()

    def upload(self):
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
        self._handle_response(requests.delete(self.location, verify=self.ssl_verify, headers=self.header))
        return True
