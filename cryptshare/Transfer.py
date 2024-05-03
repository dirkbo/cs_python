import json

import requests

import cryptshare.TransferFile as TransferFile
import cryptshare.TransferSettings as TransferSettings
from cryptshare.ApiRequestHandler import ApiRequestHandler


class Transfer(ApiRequestHandler):
    location = ""
    files = []

    def __init__(
        self,
        header,
        to,
        cc,
        bcc,
        settings: TransferSettings.TransferSettings,
        ssl_verify=True,
    ):
        self.header = header
        self.cc = cc
        self.to = to
        self.bcc = bcc
        self.sender = settings.sender
        self.send = False
        self.ssl_verify = ssl_verify

    def set_location(self, location_url):
        self.location = location_url

    def set_sender(self, sender):
        self.sender = sender

    def set_to_recipient(self, recipients):
        self.to = recipients

    def set_cc_recipient(self, recipients):
        self.cc = recipients

    def set_bcc_recipient(self, recipients):
        self.bcc = recipients

    def upload_file(self, path):
        file = TransferFile.TransferFile(path, self.header, ssl_verify=self.ssl_verify)
        r = self._handle_response(
            requests.post(
                self.location + "/files",
                verify=self.ssl_verify,
                headers=self.header,
                json=file.data(),
            )
        )
        file.set_location(r)
        file.upload()
        self.files.append(file)
        return file

    def delete_file(self, file: TransferFile):
        file.delete_upload()
        self.files.remove(file)

    def get_recipients(self):
        return {"bcc": self.bcc, "cc": self.cc, "to": self.to}

    def get_sender(self):
        return {"name": self.sender.name, "phone": self.sender.phone}

    def get_data(self):
        return {"sender": self.get_sender(), "recipients": self.get_recipients()}

    def get_transfer_settings(self):
        r = self._handle_response(requests.get(self.location, verify=self.ssl_verify, headers=self.header))
        return r

    def edit_transfer_settings(self, transfer_settings):
        r = self._handle_response(
            requests.patch(
                self.location,
                json=transfer_settings.data(),
                verify=self.ssl_verify,
                headers=self.header,
            )
        )
        return r

    def send_transfer(self):
        r = self._handle_response(requests.post(self.location, verify=self.ssl_verify, headers=self.header))
        self.location = r
        return r

    def get_transfer_status(self):
        r = self._handle_response(requests.get(self.location, verify=self.ssl_verify, headers=self.header))
        return r
