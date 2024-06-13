import hashlib
import itertools
import json
import logging
import os
from datetime import datetime

from cryptshare.base_client import CryptshareBaseClient
from cryptshare.download import CryptshareDownload
from cryptshare.notification_message import CryptshareNotificationMessage
from cryptshare.sender import CryptshareSender
from cryptshare.transfer import CryptshareTransfer
from cryptshare.transfer_policy import CryptshareTransferPolicy
from cryptshare.transfer_security_mode import (
    CryptshareTransferSecurityMode,
    OneTimePaswordSecurityModes,
)
from cryptshare.transfer_settings import CryptshareTransferSettings

logger = logging.getLogger(__name__)

TARGET_API_VERSION = "1.9"
# Default API Version to use with Cryptshare REST-API


class CryptshareClient(CryptshareBaseClient):
    _sender: CryptshareSender = None

    def set_sender(self, sender_email: str, sender_name: str = "REST-API Sender", sender_phone: str = "0"):
        logger.debug(f"Setting Cryptshare Client sender to {sender_email}")
        self.read_client_store()
        self._sender = CryptshareSender(sender_name, sender_phone, sender_email)
        self.header.verification_token = self.get_verification_from_store(sender_email)

    @property
    def sender(self) -> CryptshareSender:
        return self._sender

    @property
    def sender_email(self) -> str:
        return self._sender.email

    def request_code(self) -> None:
        path = self.api_path("users") + self.sender_email + "/verification/code/email"
        logger.info(f"Requesting verification code for {self.sender_email} from {path}")
        self._request("POST", path, verify=self.ssl_verify, headers=self.header.request_header)

    def verify_code(self, code: str) -> bool:
        url = f"{self.api_path('users')}{self.sender_email}/verification/token"
        logger.info(f"Verifying code {code} for {self.sender_email} from {url} to obtain verification token")
        r = self._request(
            "POST",
            url,
            json={"verificationCode": code},
            verify=self.ssl_verify,
            headers=self.header.request_header,
        )
        verification_token = r.get("token")
        logger.debug(f"Storing verification token for {self.sender_email} in client store")
        self.set_verification_in_store(self.sender_email, verification_token)
        logger.debug(f"Setting verification token for {self.sender_email} in client headers")
        self.header.verification_token = verification_token
        return True

    def get_verification_from_store(self, email: str = None):
        if email is None:
            email = self.sender_email
        return super().get_verification_from_store(email)

    def is_verified(self) -> bool:
        path = f"{self.api_path('users')}{self.sender_email}/verification"
        logger.info(f"Checking if {self.sender_email} is verified from {path}")

        r = self._request(
            "GET",
            path,
            verify=self.ssl_verify,
            headers=self.header.request_header,
        )
        return r.get("verified", False)

    def get_verification(self) -> dict:
        path = f"{self.api_path('users')}{self.sender_email}/verification"
        logger.info(f"Getting verification status for {self.sender_email} from {path}")

        r = self._request(
            "GET",
            path,
            verify=self.ssl_verify,
            headers=self.header.request_header,
        )
        return r

    def start_transfer(self, recipients, settings: CryptshareTransferSettings) -> CryptshareTransfer:
        logger.debug(f"Starting transfer for {self.sender_email} to {recipients} with settings {settings}")
        transfer = CryptshareTransfer(
            settings,
            to=recipients.get("to"),
            cc=recipients.get("cc"),
            bcc=recipients.get("bcc"),
            cryptshare_client=self,
        )
        transfer.start_transfer_session()
        transfer.update_transfer_settings(settings)
        return transfer

    def download_transfer(self, transfer_id, password) -> CryptshareDownload:
        logger.debug(f"Downloading transfer {transfer_id} from {self._server}")
        return CryptshareDownload(self, transfer_id, password)

    def get_transfers(self) -> dict:
        path = self.api_path("users") + self.sender_email + "/transfers"
        logger.info(f"Getting transfers for {self.sender_email} from {path}")
        r = self._request(
            "GET",
            path,
            verify=self.ssl_verify,
            headers=self.header.request_header,
        )
        return r

    def transfer_status(
        self,
        transfer_tracking_id: str = None,
        sender_name: str = None,
        sender_phone: str = None,
        sender_email: str = None,
    ):
        #  Reads existing verifications from the 'store' file if any
        self.read_client_store()

        #  request client id from server if no client id exists
        #  Both branches also react on the REST API not licensed
        if self.exists_client_id() is False:
            self.request_client_id()

        if self._sender is None:
            if sender_email is None:
                print("Sender email is required.")
                return
            sender = CryptshareSender(sender_name, sender_phone, sender_email)
            sender.setup_and_verify_sender(self)
            self._sender = sender

        if transfer_tracking_id is None:
            all_transfers = self.get_transfers()
            logger.debug("Transfer status for all transfers\n")
            transfer_status_list = []
            for list_transfer in all_transfers:
                tracking_id = list_transfer["trackingId"]
                transfer = CryptshareTransfer(CryptshareTransferSettings(self._sender), tracking_id=tracking_id)
                transfer = transfer.get_transfer_status(self)
                transfer_status_list.append({"trackingID": tracking_id, "status": transfer["status"]})
            return transfer_status_list

        logger.debug(f"Transfer status for transfer {transfer_tracking_id}\n")
        transfer = CryptshareTransfer(CryptshareTransferSettings(self._sender), tracking_id=transfer_tracking_id)
        transfer_status = transfer.get_transfer_status(self)
        return transfer_status

    def get_policy(self, recipients) -> CryptshareTransferPolicy:
        path = self.api_path("users") + self.sender_email + "/transfer-policy"
        logger.info(f"Getting policy for {self.sender_email} and  {recipients} from {path}")
        r = self._request(
            "POST",
            path,
            verify=self.ssl_verify,
            headers=self.header.extra_header({"Content-Type": "application/json"}),
            json={"recipients": recipients},
        )
        return CryptshareTransferPolicy(r)

    def send_transfer(
        self,
        transfer_password: str,
        expiration_date: datetime,
        files: str,
        recipients: list[str] = None,
        cc: list[str] = None,
        bcc: list[str] = None,
        subject: str = "",
        message: str = "",
        sender_email: str = None,
        sender_name: str = "",
        sender_phone: str = "",
        **kwargs,  # Additional Transfer settings, CryptshareTransferSettings documentation
    ) -> [CryptshareTransfer, None]:
        """Send a transfer using the Cryptshare server."""

        if not recipients:
            recipients = []
        if not cc:
            cc = []
        if not bcc:
            bcc = []

        transformed_recipients = [{"mail": recipient} for recipient in recipients]
        transformed_cc_recipients = [{"mail": recipient} for recipient in cc]
        transformed_bcc_recipients = [{"mail": recipient} for recipient in bcc]
        all_recipients = list(itertools.chain(recipients, cc, bcc))
        # All recipients list needed for policy request

        if self._sender is None:
            if sender_email is None:
                print("Sender email is required.")
                return
            sender = CryptshareSender(sender_name, sender_phone, sender_email)
            sender.setup_and_verify_sender(self)
            self._sender = sender

        # ToDo: show password rules to user, when asking for password
        transfer_security_mode = CryptshareTransferSecurityMode(
            password=transfer_password, mode=OneTimePaswordSecurityModes.MANUAL
        )
        if transfer_password == "" or transfer_password is None:
            transfer_password = self.get_password()
            print(f"Generated Password to receive Files: {transfer_password}")
            transfer_security_mode = CryptshareTransferSecurityMode(password=transfer_password)
        else:
            passwort_validated_response = self.validate_password(transfer_password)
            valid_password = passwort_validated_response.get("valid")
            if not valid_password:
                print("Passwort is not valid.")
                password_rules = self.get_password_rules()
                logger.debug(f"Passwort rules:\n{password_rules}")
                return

        transfer_policy = self.get_policy(all_recipients)
        if not transfer_policy.is_allowed:
            print("Policy not valid.")
            logger.debug(f"Policy response: {transfer_policy}")
            return

        #  Transfer definition
        subject = subject if subject != "" else None
        notification = CryptshareNotificationMessage(message, subject)
        # ToDo: Make sure detected Language is available as Language Pack on the Cryptshare Server
        settings = CryptshareTransferSettings(
            self._sender,
            notification_message=notification,
            send_download_notifications=True,
            security_mode=transfer_security_mode,
            expiration_date=expiration_date,
            recipientLanguage=notification.language,
            senderLanguage=self._sender.language,
            **kwargs,
        )

        #  Start of transfer on server side
        transfer = CryptshareTransfer(
            settings,
            to=transformed_recipients,
            cc=transformed_cc_recipients,
            bcc=transformed_bcc_recipients,
            cryptshare_client=self,
        )
        transfer.set_generated_password(transfer_password)
        transfer.start_transfer_session()
        for file in files:
            transfer.upload_file(file)

        pre_transfer_info = transfer.get_transfer_settings(self)
        logger.debug(f"Pre-Transfer info: \n{pre_transfer_info}")
        transfer.send_transfer(self)
        post_transfer_info = transfer.get_transfer_status(self)
        logger.debug(f" Post-Transfer info: \n{post_transfer_info}")
        print(f"Transfer {transfer.tracking_id} uploaded successfully.")
        return transfer
