import hashlib
import itertools
import json
import logging
import os
from datetime import datetime

import requests

from cryptshare.CryptshareDownload import CryptshareDownload
from cryptshare.CryptshareSender import CryptshareSender
from cryptshare.CryptshareHeader import CryptshareHeader
from cryptshare.Transfer import Transfer
from cryptshare.TransferSettings import TransferSettings
from cryptshare.ApiRequestHandler import ApiRequestHandler
from cryptshare.NotificationMessage import NotificationMessage
from cryptshare.SecurityMode import SecurityMode

logger = logging.getLogger(__name__)


class CryptshareClient(ApiRequestHandler):
    header = CryptshareHeader()
    _sender: CryptshareSender = None
    _server = ""
    _api_paths = {
        "users": "/api/users/",
        "clients": "/api/clients",
        "products": "/api/products/",
        "password_requirements": "/api/password/requirements",
        "password": "/api/password",
    }
    _client_store = {}

    def __init__(self, server, client_store_path="client_store.json", ssl_verify=True):
        logger.info(f"Initialising Cryptshare Client for server: {server}")
        self._server = server
        self.client_store_path = client_store_path
        self.ssl_verify = ssl_verify

    @property
    def server(self):
        return self._server

    @property
    def server_hash(self):
        return hashlib.shake_256(self._server.encode("utf-8")).hexdigest(8)

    @server.setter
    def server(self, server: str):
        logger.info(f"Setting server to {server}")
        self._server = server

    def api_path(self, path: str):
        return f"{self._server}{self._api_paths.get(path, '')}"

    def reset_headers(self):
        logger.debug("Resetting headers")
        self.header = CryptshareHeader()

    def get_verification_from_store(self, email: str = None):
        if email is None:
            email = self.sender_email
        hashed_email = hashlib.shake_256(email.encode("utf-8")).hexdigest(16)
        if hashed_email in self._client_store:
            logger.debug(f"Verification token for {email} found in client store")
            return self._client_store.get(hashed_email)
        logger.debug(f"No Verification token for {email} found in client store")
        return ""

    def set_verification_in_store(self, email: str, verification_token: str):
        hashed_email = hashlib.shake_256(email.encode("utf-8")).hexdigest(16)
        logger.debug(f"Setting verification token for {email} in client store")
        self._client_store.update({hashed_email: verification_token})

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

    def get_emails(self) -> list[str]:
        logger.debug("Getting emails from client store")
        return_list = []
        for a in self._client_store:
            if "@" in a:
                return_list.append(a)
        return return_list

    def delete_email(self, email: str):
        logger.debug(f"Deleting email {email} from client store")
        if email in self._client_store:
            self._client_store.remove(email)

    def request_code(self) -> None:
        path = self.api_path("users") + self.sender_email + "/verification/code/email"
        logger.info(f"Requesting verification code for {self.sender_email} from {path}")
        self._handle_response(
            requests.post(
                path,
                verify=self.ssl_verify,
                headers=self.header.request_header,
            )
        )

    def verify_code(self, code: str) -> bool:
        url = f"{self.api_path('users')}{self.sender_email}/verification/token"
        logger.info(f"Verifying code {code} for {self.sender_email} from {url} to obtain verification token")
        r = self._handle_response(
            requests.post(
                url,
                json={"verificationCode": code},
                verify=self.ssl_verify,
                headers=self.header.request_header,
            )
        )
        verification_token = r.get("token")
        logger.debug(f"Storing verification token for {self.sender_email} in client store")
        self.set_verification_in_store(self.sender_email, verification_token)
        logger.debug(f"Setting verification token for {self.sender_email} in client headers")
        self.header.verification_token = verification_token
        return True

    def is_verified(self) -> bool:
        path = f"{self.api_path('users')}{self.sender_email}/verification"
        logger.info(f"Checking if {self.sender_email} is verified from {path}")

        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.request_header,
            )
        )
        return r.get("verified", False)

    def get_verification(self) -> dict:
        path = f"{self.api_path('users')}{self.sender_email}/verification"
        logger.info(f"Getting verification status for {self.sender_email} from {path}")

        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.request_header,
            )
        )
        return r

    def cors(self, origin: str) -> None:
        path = f"{self.api_path('products')}api.rest/cors"
        logger.info(f"Checking CORS for origin {origin} and {path}")
        self.header.origin = origin

        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.request_header_cors,
            )
        )
        logger.info(f"CORS is active for origin {origin}: {r.get('active')}")

    def exists_client_id(self) -> bool:
        logger.debug("Checking if client ID exists in Headers")
        if "X-CS-ClientId" in self.header.request_header:
            return True
        return False

    def start_transfer(self, recipients, settings: TransferSettings) -> Transfer:
        logger.debug(f"Starting transfer for {self.sender_email} to {recipients} with settings {settings}")
        transfer = Transfer(
            self.header,
            recipients.get("to"),
            recipients.get("cc"),
            recipients.get("bcc"),
            settings,
            ssl_verify=self.ssl_verify,
        )
        path = f"{self.api_path('users')}{self.sender_email}/transfer-sessions"
        logger.info(f"Starting transfer for {self.sender_email} from {path}")
        r = self._handle_response(
            requests.post(
                path,
                verify=self.ssl_verify,
                headers=self.header.extra_header({"Content-Type": "application/json"}),
                json=transfer.get_data(),
            )
        )
        transfer.set_location(r)
        transfer.edit_transfer_settings(settings)
        return transfer

    def request_client_id(self):
        path = self.api_path("clients")
        logger.info(f"Requesting client ID from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.request_header,
            )
        )
        logger.debug("Storing client ID in client store")
        self.header.client_id = r.get("clientId")
        logger.debug("Setting client ID in client headers")
        self._client_store.update({"X-CS-ClientId": r.get("clientId")})

    @property
    def server_client_store_path(self):
        client_store = self.client_store_path
        path = os.path.splitext(client_store)
        client_store = f"{path[0]}_{self.server_hash}{path[1]}"
        return client_store

    def read_client_store(self):
        logger.debug(f"Reading client store from {self.server_client_store_path}")
        try:
            with open(self.server_client_store_path, "r") as json_file:
                try:
                    self._client_store = json.load(json_file)
                except Exception as e:
                    print(f"Failed to read store: {e}")
            if "X-CS-ClientId" in self._client_store:
                self.header.client_id = self._client_store.get("X-CS-ClientId")
        except IOError:
            logger.warning(f"Failed to read client store from {self.server_client_store_path}")
            return ""

    def write_client_store(self):
        logger.debug(f"Writing client store to {self.server_client_store_path}")
        try:
            with open(self.server_client_store_path, "w") as outfile:
                json.dump(self._client_store, outfile, indent=4)
            outfile.close()
        except IOError:
            logger.warning(f"Failed to write client store to {self.server_client_store_path}")

    def get_password_rules(self):
        path = self.api_path("password_requirements")
        logger.info(f"Getting password rules from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.request_header,
            )
        )
        return r

    def get_transfers(self) -> dict:
        path = self.api_path("users") + self.sender_email + "/transfers"
        logger.info(f"Getting transfers for {self.sender_email} from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.request_header,
            )
        )
        return r

    def validate_password(self, password):
        path = self.api_path("password")
        logger.info(f"Validating password for {self.sender_email} from {path}")
        r = self._handle_response(
            requests.post(
                path,
                verify=self.ssl_verify,
                headers=self.header.extra_header({"Content-Type": "application/json"}),
                json={"password": password},
            )
        )
        return r

    def get_password(self):
        path = self.api_path("password")
        logger.info(f"Getting generated password from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.request_header,
            )
        )
        return r

    def get_policy(self, recipients):
        path = self.api_path("users") + self.sender_email + "/transfer-policy"
        logger.info(f"Getting policy for {self.sender_email} and  {recipients} from {path}")
        r = self._handle_response(
            requests.post(
                path,
                verify=self.ssl_verify,
                headers=self.header.extra_header({"Content-Type": "application/json"}),
                json={"recipients": recipients},
            )
        )
        return r

    def download_transfer(self, transfer_id, password) -> CryptshareDownload:
        logger.debug(f"Downloading transfer {transfer_id} from {self._server}")
        return CryptshareDownload(self, transfer_id, password)

    def transfer_status(
        self,
        transfer_transfer_id: str = None,
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

        if transfer_transfer_id is None:
            all_transfers = self.get_transfers()
            logger.debug("Transfer status for all transfers\n")
            transfer_status_list = []
            for list_transfer in all_transfers:
                tracking_id = list_transfer["trackingId"]
                transfer = Transfer(self.header, [], [], [], TransferSettings(self.sender_email))
                status_location = f"{self.server}/api/users/{self.sender_email}/transfers/{tracking_id}"
                transfer.set_location(status_location)
                transfer = transfer.get_transfer_status()
                status = {"trackingID": tracking_id, "status": transfer["status"]}
                transfer_status_list.append(status)
            return transfer_status_list

        logger.debug(f"Transfer status for transfer {transfer_transfer_id}\n")
        transfer = Transfer(self.header, [], [], [], TransferSettings(self.sender_email))
        status_location = f"{self.api_path("users")}{self.sender_email}/transfers/{transfer_transfer_id}"
        transfer.set_location(status_location)
        transfer = transfer.get_transfer_status()
        status = transfer["status"]
        return status

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
    ) -> None:
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
        transfer_security_mode = SecurityMode(password=transfer_password, mode="MANUAL")
        if transfer_password == "" or transfer_password is None:
            transfer_password = self.get_password().get("password")
            print(f"Generated Password to receive Files: {transfer_password}")
            transfer_security_mode = SecurityMode(password=transfer_password, mode="GENERATED")
        else:
            passwort_validated_response = self.validate_password(transfer_password)
            valid_password = passwort_validated_response.get("valid")
            if not valid_password:
                print("Passwort is not valid.")
                password_rules = self.get_password_rules()
                logger.debug(f"Passwort rules:\n{password_rules}")
                return

        policy_response = self.get_policy(all_recipients)
        valid_policy = policy_response.get("allowed", False)
        if not valid_policy:
            print("Policy not valid.")
            logger.debug(f"Policy response: {policy_response}")
            return

        #  Transfer definition
        subject = subject if subject != "" else None
        notification = NotificationMessage(message, subject)
        settings = TransferSettings(
            self._sender,
            notification_message=notification,
            send_download_notifications=True,
            security_mode=transfer_security_mode,
            expiration_date=expiration_date.astimezone().isoformat(),
        )

        #  Start of transfer on server side
        transfer = self.start_transfer(
            {
                "bcc": transformed_bcc_recipients,
                "cc": transformed_cc_recipients,
                "to": transformed_recipients,
            },
            settings,
        )
        for file in files:
            transfer.upload_file(self, file)

        pre_transfer_info = transfer.get_transfer_settings()
        logger.debug(f"Pre-Transfer info: \n{pre_transfer_info}")
        transfer.send_transfer()
        post_transfer_info = transfer.get_transfer_status()
        logger.debug(f" Post-Transfer info: \n{post_transfer_info}")
        transfer_id = transfer.get_transfer_id()
        print(f"Transfer {transfer_id} uploaded successfully.")