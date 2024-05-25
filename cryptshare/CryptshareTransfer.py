import hashlib
import logging
import os

from cryptshare import CryptshareClient, CryptshareSender
from cryptshare.CryptshareApiRequests import CryptshareApiRequests
from cryptshare.CryptshareTransferSettings import CryptshareTransferSettings
from cryptshare.CryptshareValidators import CryptshareValidators

logger = logging.getLogger(__name__)


class TransferFile(CryptshareApiRequests):
    _cryptshare_client: CryptshareClient = None
    _location: str = ""
    _file_id: str = ""
    _tracking_id: str = ""
    size: int
    name: str
    path: str
    checksum: str

    def __init__(self, path: str, session_tracking_id: str, cryptshare_client: CryptshareClient):
        logger.debug(f"Initialising Cryptshare TransferFile object for file: {path}")
        self.size = os.stat(path).st_size
        self.name = os.path.basename(path)
        self.path = path
        self._cryptshare_client = cryptshare_client
        self._tracking_id = session_tracking_id
        self.calculate_checksum()

    def calculate_checksum(self):
        logger.debug("Calculating checksum")  # Calculate file hashsum
        with open(self.path, "rb") as data:
            file_content = data.read()
            self.checksum = hashlib.sha256(file_content).hexdigest()

    @staticmethod
    def get_file_id_from_returned_url(url: str):
        logger.debug("Getting file ID")
        try:
            file_id = url.split("/")[-1]
        except IndexError:
            logger.error("No file ID found in location URL")
            return None
        else:
            return file_id

    @property
    def transfer_session_url(self):
        return f"{self._cryptshare_client.api_path('users')}{self._cryptshare_client.sender_email}/transfer-sessions/{self._tracking_id}"

    def data(self):
        logger.debug("Returning TransferFile data")
        return {"fileName": self.name, "size": self.size, "checksum": self.checksum}

    def announce_upload(self):
        url = f"{self.transfer_session_url}/files"
        logger.info(f"Announcing file {self.name} upload POST {url}")
        r = self._request(
            "POST",
            url,
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.request_header,
            json=self.data(),
        )
        logger.debug(f"File upload announced at {r}")
        self._file_id = self.get_file_id_from_returned_url(r)
        logger.debug(f"File ID: {self._file_id}")

    def upload_file_content(self):
        url = f"{self.transfer_session_url}/files/{self._file_id}/content"
        logger.info(f"Uploading file {self.name} content to PUT {url}")
        data = open(self.path, "rb").read()
        self._request(
            "PUT",
            url,
            data=data,
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.request_header,
        )
        return True

    def delete_upload(self):
        url = f"{self.transfer_session_url}"
        logger.debug(f"Deleting uploaded file {self.name}  DELETE {url}")
        # ToDo: Will it delete the file or the transfer session?
        self._request(
            "DELETE",
            url,
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.request_header,
        )
        return True


class CryptshareTransfer(CryptshareApiRequests):
    _cryptshare_client: CryptshareClient = None
    files = []
    tracking_id: str = ""
    _settings: CryptshareTransferSettings
    sender: CryptshareSender = None
    _session_is_open: bool = False  # Open transfer sessions allow adding and removing files and updating settings
    _generated_password: str = None

    def __init__(
        self,
        settings: CryptshareTransferSettings,
        to: list[[dict[str, str]]] = None,
        cc: list[[dict[str, str]]] = None,
        bcc: list[[dict[str, str]]] = None,
        tracking_id: str = None,
        cryptshare_client: CryptshareClient = None,
    ):
        logger.debug("Initialising Cryptshare Transfer object")
        self.cc = cc if cc else []
        self.to = to if to else []
        self.bcc = bcc if bcc else []
        self.sender = settings.sender
        if not CryptshareValidators.is_valid_tracking_id_or_blank(tracking_id):
            raise ValueError("Invalid tracking ID")
        self.tracking_id = tracking_id if tracking_id else ""
        self._cryptshare_client = cryptshare_client if cryptshare_client else None
        self._settings = settings
        self.send = False

    def get_transfer_session_url(self, cryptshare_client: CryptshareClient = None):
        self._cryptshare_client = cryptshare_client if cryptshare_client else self._cryptshare_client
        # Update transfer's cryptshare client, if provided

        return f"{self._cryptshare_client.api_path('users')}{self._settings.sender.email}/transfer-sessions/{self.tracking_id}"

    def get_transfer_status_url(self, cryptshare_client: CryptshareClient = None):
        self._cryptshare_client = cryptshare_client if cryptshare_client else self._cryptshare_client
        # Update transfer's cryptshare client, if provided

        return f"{self._cryptshare_client.api_path('users')}{self._settings.sender.email}/transfers/{self.tracking_id}"

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

    def start_transfer_session(self, cryptshare_client: CryptshareClient = None):
        """Starts a new transfer session"""
        if self._session_is_open:
            logger.error("Cryptshare Transfer Session is open, can't restart it")
            return None

        self._cryptshare_client = cryptshare_client if cryptshare_client else self._cryptshare_client
        # Update transfer's cryptshare client, if provided

        logger.debug("Starting transfer session")
        logger.debug(f"Transfer settings: {self._settings.data()}")
        path = f"{self._cryptshare_client.api_path('users')}{self._settings.sender.email}/transfer-sessions"
        logger.info(f"Starting transfer for {self._settings.sender.email}  POST {path}")
        r = self._request(
            "POST",
            path,
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.extra_header({"Content-Type": "application/json"}),
            json=self.get_sender_and_recipients(),
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

    def upload_file(self, path: str, cryptshare_client: CryptshareClient = None):
        if not self._session_is_open:
            logger.error("Cryptshare Transfer Session is not open, can't upload file")
            return None

        self._cryptshare_client = cryptshare_client if cryptshare_client else self._cryptshare_client
        # Update transfer's cryptshare client, if provided

        file = TransferFile(path, self.tracking_id, self._cryptshare_client)
        file.announce_upload()
        file.upload_file_content()
        self.files.append(file)
        return file

    def delete_file(self, file: TransferFile, cryptshare_client: CryptshareClient = None):
        if not self._session_is_open:
            logger.error("Cryptshare Transfer Session is not open, can't upload file")
            return None

        self._cryptshare_client = cryptshare_client if cryptshare_client else self._cryptshare_client
        # Update transfer's cryptshare client, if provided

        logger.debug(f"Deleting file {file.name}")
        file.delete_upload()
        self.files.remove(file)

    def delete_transfer_session(self):
        if self._session_is_open:
            path = self.get_transfer_session_url()
            logger.debug(f"Deleting transfer session DELETE {path}")
            self._request(
                "DELETE",
                path,
                verify=self._cryptshare_client.ssl_verify,
                headers=self._cryptshare_client.header.request_header,
            )

    def __del__(self):
        logger.debug("Deleting Cryptshare Transfer object")
        self.delete_transfer_session()

    def get_recipients(self) -> dict:
        logger.debug("Getting recipients data")
        return {"bcc": self.bcc, "cc": self.cc, "to": self.to}

    def get_sender(self) -> dict:
        logger.debug("Getting sender data")
        return self.sender.data()

    def get_sender_and_recipients(self) -> dict:
        logger.debug("Getting transfer sender and recipient data")
        return {"sender": self.get_sender(), "recipients": self.get_recipients()}

    def get_transfer_settings(self, cryptshare_client: CryptshareClient = None):
        if not self._session_is_open:
            logger.error("Cryptshare Transfer Session is not open, can't upload file")
            return None

        self._cryptshare_client = cryptshare_client if cryptshare_client else self._cryptshare_client
        # Update transfer's cryptshare client, if provided

        path = self.get_transfer_session_url()
        logger.info(f"Getting transfer settings from GET {path}")
        r = self._request(
            "GET",
            path,
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.request_header,
        )
        return r

    def update_transfer_settings(
        self, transfer_settings: CryptshareTransferSettings = None, cryptshare_client: CryptshareClient = None
    ):
        if not self._session_is_open:
            logger.error("Cryptshare Transfer Session is not open, can't change Transfer Settings")
            return None

        self._cryptshare_client = cryptshare_client if cryptshare_client else self._cryptshare_client
        # Update transfer's cryptshare client, if provided
        self._settings = transfer_settings if transfer_settings else self._settings
        # Update transfer's settings, if provided

        path = self.get_transfer_session_url()
        logger.debug(f"Editing transfer settings PATCH {path}")
        r = self._request(
            "PATCH",
            path,
            json=self._settings.data(),
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.request_header,
        )
        return r

    def send_transfer(self, cryptshare_client: CryptshareClient = None):
        if not self._session_is_open:
            logger.error("Cryptshare Transfer Session is not open, can't change Transfer Settings")
            return None

        self._cryptshare_client = cryptshare_client if cryptshare_client else self._cryptshare_client
        # Update transfer's cryptshare client, if provided

        path = self.get_transfer_session_url()
        logger.debug(f"Sending transfer POST {path}")
        r = self._request(
            "POST",
            path,
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.request_header,
        )
        self._session_is_open = False
        return r

    def get_transfer_status(self, cryptshare_client: CryptshareClient = None):
        self._cryptshare_client = cryptshare_client if cryptshare_client else self._cryptshare_client
        # Update transfer's cryptshare client, if provided

        path = self.get_transfer_status_url()
        logger.debug(f"Getting transfer status GET {path}")
        r = self._request(
            "GET",
            path,
            verify=self._cryptshare_client.ssl_verify,
            headers=self._cryptshare_client.header.request_header,
        )
        return r
