import logging

import requests

from cryptshare import CryptshareClient, CryptshareSender
from cryptshare.ApiRequestHandler import ApiRequestHandler
from cryptshare.CryptshareValidators import CryptshareValidators
from cryptshare.TransferFile import TransferFile
from cryptshare.TransferSettings import TransferSettings

logger = logging.getLogger(__name__)


class CryptshareTransfer(ApiRequestHandler):
    location = ""
    files = []
    tracking_id: str = ""
    _settings: TransferSettings
    sender: CryptshareSender = None
    _session_is_open: bool = False
    _generated_password: str = None

    def __init__(
        self,
        settings: TransferSettings,
        to: list[[dict[str, str]]] = None,
        cc: list[[dict[str, str]]] = None,
        bcc: list[[dict[str, str]]] = None,
        tracking_id: str = None,
    ):
        logger.debug("Initialising Cryptshare Transfer object")
        self.cc = cc if cc else []
        self.to = to if to else []
        self.bcc = bcc if bcc else []
        self.sender = settings.sender
        if not CryptshareValidators.is_valid_tracking_id_or_blank(tracking_id):
            raise ValueError("Invalid tracking ID")
        self.tracking_id = tracking_id if tracking_id else ""
        self._settings = settings
        self.send = False

    def get_transfer_session_url(self, cryptshare_client: CryptshareClient):
        return (
            f"{cryptshare_client.api_path('users')}{self._settings.sender.email}/transfer-sessions/{self.tracking_id}"
        )

    def get_transfer_status_url(self, cryptshare_client: CryptshareClient):
        return f"{cryptshare_client.api_path('users')}{self._settings.sender.email}/transfers/{self.tracking_id}"

    def set_generated_password(self, password: str):
        """
        Set the generated password for the transfer session if the security mode is set to GENERATED
        :param password:
        :return:
        """
        if self._settings.security_mode.mode == "GENERATED":
            self._generated_password = password

    def get_generated_password(self):
        """
        Get the generated password for the transfer session if the security mode is set to GENERATED
        :return:
        """
        if self._settings.security_mode.mode == "GENERATED":
            return self._generated_password
        return None

    def start_transfer_session(self, cryptshare_client: CryptshareClient, settings: TransferSettings = None):
        """Starts a new transfer session"""
        self._settings = settings if settings else self._settings

        logger.debug("Starting transfer session")
        path = f"{cryptshare_client.api_path('users')}{self._settings.sender.email}/transfer-sessions"
        logger.info(f"Starting transfer for {self._settings.sender.email} from {path}")
        r = self._handle_response(
            requests.post(
                path,
                verify=cryptshare_client.ssl_verify,
                headers=cryptshare_client.header.extra_header({"Content-Type": "application/json"}),
                json=self.get_sender_and_recipients(),
            )
        )
        location = r
        logger.debug(f"Transfer session started at {location}")
        self.tracking_id = self.get_transfer_id_from_returned_url(location)
        self._session_is_open = True
        return r

    @staticmethod
    def get_transfer_id_from_returned_url(url: str):
        logger.debug("Getting tracking ID")
        try:
            tracking_id = url.split("/")[-1]
        except IndexError:
            logger.error("No tracking ID found in location URL")
            return None
        else:
            if not CryptshareValidators.is_valid_tracking_id(tracking_id):
                raise ValueError("Unable to retrieve transfer sessions tracking id")
            return tracking_id

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

    def upload_file(self, cryptshare_client: CryptshareClient, path: str):
        if not self._session_is_open:
            logger.error("Cryptshare Transfer Session is not open, can't upload file")
            return None
        url = f"{self.get_transfer_session_url(cryptshare_client)}/files"
        logger.debug(f"Uploading file {path} to {url}")
        file = TransferFile(path)
        r = self._handle_response(
            requests.post(
                url,
                verify=cryptshare_client.ssl_verify,
                headers=cryptshare_client.header.request_header,
                json=file.data(),
            )
        )
        file.set_location(r)
        file.upload(cryptshare_client)
        self.files.append(file)
        return file

    def delete_file(self, cryptshare_client, file: TransferFile):
        if not self._session_is_open:
            logger.error("Cryptshare Transfer Session is not open, can't upload file")
            return None
        logger.debug(f"Deleting file {file.name}")
        file.delete_upload(cryptshare_client)
        self.files.remove(file)

    def get_recipients(self) -> dict:
        logger.debug("Getting recipients data")
        return {"bcc": self.bcc, "cc": self.cc, "to": self.to}

    def get_sender(self) -> dict:
        logger.debug("Getting sender data")
        return self.sender.data()

    def get_sender_and_recipients(self) -> dict:
        logger.debug("Getting transfer sender and recipient data")
        return {"sender": self.get_sender(), "recipients": self.get_recipients()}

    def get_transfer_settings(self, cryptshare_client: CryptshareClient):
        if not self._session_is_open:
            logger.error("Cryptshare Transfer Session is not open, can't upload file")
            return None
        path = self.get_transfer_session_url(cryptshare_client)
        logger.info(f"Getting transfer settings from GET {path}")
        r = self._handle_response(
            requests.get(path, verify=cryptshare_client.ssl_verify, headers=cryptshare_client.header.request_header)
        )
        return r

    def edit_transfer_settings(self, cryptshare_client: CryptshareClient, transfer_settings):
        if not self._session_is_open:
            logger.error("Cryptshare Transfer Session is not open, can't upload file")
            return None
        path = self.get_transfer_session_url(cryptshare_client)
        logger.debug(f"Editing transfer settings PATCH {path}")
        r = self._handle_response(
            requests.patch(
                path,
                json=transfer_settings.data(),
                verify=cryptshare_client.ssl_verify,
                headers=cryptshare_client.header.request_header,
            )
        )
        return r

    def send_transfer(self, cryptshare_client: CryptshareClient):
        path = self.get_transfer_session_url(cryptshare_client)
        logger.debug(f"Sending transfer POST {path}")
        r = self._handle_response(
            requests.post(path, verify=cryptshare_client.ssl_verify, headers=cryptshare_client.header.request_header)
        )
        self._session_is_open = False
        return r

    def get_transfer_status(self, cryptshare_client: CryptshareClient):
        path = self.get_transfer_status_url(cryptshare_client)
        logger.debug(f"Getting transfer status GET {path}")
        r = self._handle_response(
            requests.get(path, verify=cryptshare_client.ssl_verify, headers=cryptshare_client.header.request_header)
        )
        return r