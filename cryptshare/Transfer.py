import logging

import requests

import cryptshare.TransferFile as TransferFile
import cryptshare.TransferSettings as TransferSettings
from cryptshare.ApiRequestHandler import ApiRequestHandler

logger = logging.getLogger(__name__)


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
        logger.debug("Initialising Cryptshare Transfer object")
        self.header = header
        self.cc = cc
        self.to = to
        self.bcc = bcc
        self.sender = settings.sender
        self.send = False
        self.ssl_verify = ssl_verify

    def set_location(self, location_url):
        logger.debug(f"Setting location to {location_url}")
        self.location = location_url

    def get_transfer_id(self):
        logger.debug("Getting transfer ID")
        try:
            return self.location.split("/")[-1]
        except IndexError:
            logger.error("No transfer ID found in location URL")
            return None

    def set_sender(self, sender):
        logger.debug(f"Setting sender to {sender.name}")
        self.sender = sender

    def set_to_recipient(self, recipients):
        logger.debug(f"Setting to recipients to {recipients}")
        self.to = recipients

    def set_cc_recipient(self, recipients):
        logger.debug(f"Setting cc recipients to {recipients}")
        self.cc = recipients

    def set_bcc_recipient(self, recipients):
        logger.debug(f"Setting bcc recipients to {recipients}")
        self.bcc = recipients

    def upload_file(self, path):
        logger.debug(f"Uploading file {path}")
        file = TransferFile.TransferFile(path, self.header, ssl_verify=self.ssl_verify)
        r = self._handle_response(
            requests.post(
                self.location + "/files",
                verify=self.ssl_verify,
                headers=self.header.request_header,
                json=file.data(),
            )
        )
        file.set_location(r)
        file.upload()
        self.files.append(file)
        return file

    def delete_file(self, file: TransferFile):
        logger.debug(f"Deleting file {file.name}")
        file.delete_upload()
        self.files.remove(file)

    def get_recipients(self):
        logger.debug("Getting recipients")
        return {"bcc": self.bcc, "cc": self.cc, "to": self.to}

    def get_sender(self):
        logger.debug("Getting sender")
        return self.sender.data()

    def get_data(self):
        logger.debug("Getting transfer data")
        return {"sender": self.get_sender(), "recipients": self.get_recipients()}

    def get_transfer_settings(self):
        logger.debug("Getting transfer settings")
        r = self._handle_response(
            requests.get(self.location, verify=self.ssl_verify, headers=self.header.request_header)
        )
        return r

    def edit_transfer_settings(self, transfer_settings):
        logger.debug("Editing transfer settings")
        r = self._handle_response(
            requests.patch(
                self.location,
                json=transfer_settings.data(),
                verify=self.ssl_verify,
                headers=self.header.request_header,
            )
        )
        return r

    def send_transfer(self):
        logger.debug("Sending transfer")
        r = self._handle_response(
            requests.post(self.location, verify=self.ssl_verify, headers=self.header.request_header)
        )
        self.location = r
        return r

    def get_transfer_status(self):
        logger.debug("Getting transfer status")
        r = self._handle_response(
            requests.get(self.location, verify=self.ssl_verify, headers=self.header.request_header)
        )
        return r
