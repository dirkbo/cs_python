import hashlib
import itertools
import json
import logging
import os
from datetime import datetime

from cryptshare.CryptshareApiRequests import CryptshareApiRequests
from cryptshare.CryptshareDownload import CryptshareDownload
from cryptshare.CryptshareHeader import CryptshareHeader
from cryptshare.CryptshareNotificationMessage import CryptshareNotificationMessage
from cryptshare.CryptshareSender import CryptshareSender
from cryptshare.CryptshareTransfer import CryptshareTransfer
from cryptshare.CryptshareTransferPolicy import CryptshareTransferPolicy
from cryptshare.CryptshareTransferSecurityMode import (
    CryptshareTransferSecurityMode,
    OneTimePaswordSecurityModes,
)
from cryptshare.CryptshareTransferSettings import CryptshareTransferSettings
from cryptshare.CryptshareValidators import CryptshareValidators

logger = logging.getLogger(__name__)

CURRENT_MAXIMUM_TARGET_API_VERSION = "1.9"


class CryptshareClient(CryptshareApiRequests):
    _target_api_version = CURRENT_MAXIMUM_TARGET_API_VERSION
    header: CryptshareHeader = None
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

    def __init__(self, server, client_store_path="client_store.json", target_api_version: str = None, ssl_verify=True):
        logger.info(f"Initialising Cryptshare Client for server: {server}")
        if not CryptshareValidators.is_valid_server_url(server):
            raise ValueError("Invalid Cryptshare server URL")
        self._server = server
        self.client_store_path = client_store_path
        self.ssl_verify = ssl_verify
        self._target_api_version = os.getenv("CRYPTSHARE_API_VERSION", self._target_api_version)
        if target_api_version:
            self._target_api_version = target_api_version
        self.header = CryptshareHeader(target_api_version=self._target_api_version)

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
        self.header = self.header = CryptshareHeader(target_api_version=self._target_api_version)

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
        hashed_email = hashlib.shake_256(email.encode("utf-8")).hexdigest(16)
        if hashed_email in self._client_store:
            self._client_store.remove(hashed_email)

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

    def cors(self, origin: str) -> None:
        path = f"{self.api_path('products')}api.rest/cors"
        logger.info(f"Checking CORS for origin {origin} and {path}")
        origin_header = {"Origin": origin}

        r = self._request("GET", path, verify=self.ssl_verify, headers=self.header.extra_header(origin_header))
        logger.info(f"CORS is active for origin {origin}: {r.get('active')}")

    def exists_client_id(self) -> bool:
        logger.debug("Checking if client ID exists in Headers")
        if "X-CS-ClientId" in self.header.request_header:
            return True
        return False

    def get_language_packs(self, product_key: str = "api.rest") -> list:
        # "GET https://<your-url>/api/products/<product-key>/language-packs"
        path = self.api_path("products") + f"{product_key}/language-packs"
        logger.info(f"Getting language packs from {path}")
        r = self._request(
            "GET",
            path,
            verify=self.ssl_verify,
            headers=self.header.request_header,
        )
        return r

    def get_available_languages(self, product_key: str = "api.rest") -> list:
        data = self.get_language_packs(product_key)
        return list(set([lp["locale"] for lp in data]))

    def get_terms_of_use(self) -> dict:
        # "GET https://<your-url>/api/products/<product-key>/terms-of-use"
        path = self.api_path("products") + "api.rest/legal/terms-of-use"
        logger.info(f"Getting terms of use from {path}")
        r = self._request(
            "GET",
            path,
            verify=self.ssl_verify,
            headers=self.header.request_header,
        )
        return r

    def get_imprint(self) -> dict:
        # "GET https://<your-url>/api/products/<product-key>/imprint"
        path = self.api_path("products") + "api.rest/legal/imprint"
        logger.info(f"Getting imprint from {path}")
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

    def request_client_id(self):
        path = self.api_path("clients")
        logger.info(f"Requesting client ID from {path}")
        r = self._request(
            "GET",
            path,
            verify=self.ssl_verify,
            headers=self.header.request_header,
        )
        logger.debug("Storing client ID in client store")
        self.header.client_id = r.get("clientId")
        logger.debug("Setting client ID in client headers")
        self._client_store.update({"X-CS-ClientId": r.get("clientId")})

    def set_client_id(self, client_id: str):
        logger.debug("Setting client ID in client headers")
        self.header.update_header({"X-CS-ClientId": client_id})

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
        except IOError:
            logger.warning(f"Failed to write client store to {self.server_client_store_path}")

    def get_password_rules(self):
        path = self.api_path("password_requirements")
        logger.info(f"Getting password rules from {path}")
        r = self._request(
            "GET",
            path,
            verify=self.ssl_verify,
            headers=self.header.request_header,
        )
        return r

    def get_human_readable_password_rules(self, password_rules: list = None) -> list:
        """Returning human-readable password rules from password rules list
        If whitespaces are forbidden for whitespacesDeclined
        If alphabetical sequences like "abc" are forbidden for	alphabeticalSequenceDeclined
        If numeric sequences like "123" are forbidden	numericSequenceDeclined
        If sequences found on keyboards are forbidden like "qwerty"	keyboardSequenceDeclined
        If the blocklisted characters are forbidden. (Manually configurable by the Cryptshare Server administrator)	blacklistedCharactersDeclined
        If directly repeated characters are forbidden like (Flussschifffahrt with sss and fff)	repeatedCharactersDeclined
        If common words that can be found in dictionaries are forbidden.	dictionaryWordsDeclined
        The minimum length of the password	minimumLengthRequired
        The maximum length of the password	maximumLengthRequired
        If letters are required	lettersRequired
        If special characters like !"§$ are required	specialCharactersRequired
        If upper case characters are required	upperCaseRequired
        If lower case characters are required	lowerCaseRequired
        If digits are required.

        :param password_rules: list of password rules from the server, if None, password rules are fetched from the server
        :return:
        """
        if password_rules is None:
            password_rules = self.get_password_rules()

        human_password_rules = []
        for rule in password_rules:
            if rule["name"] == "whitespacesDeclined":
                human_password_rules.append("No whitespaces allowed")
            if rule["name"] == "minimumLengthRequired":
                human_password_rules.append(f"Minimal length: {rule['details']['length']}")
            if rule["name"] == "maximumLengthRequired":
                human_password_rules.append(f"Maximal length: {rule['details']['length']}")
            if rule["name"] == "specialCharactersRequired":
                human_password_rules.append("Special characters are required")
            if rule["name"] == "upperCaseRequired":
                human_password_rules.append("Uppercase characters are required")
            if rule["name"] == "lowerCaseRequired":
                human_password_rules.append("Lowercase characters are required")
            if rule["name"] == "lettersRequired":
                human_password_rules.append("Letters are required")
            if rule["name"] == "digitsRequired":
                human_password_rules.append("Digits are required")
            if rule["name"] == "alphabeticalSequenceDeclined":
                human_password_rules.append("No alphabetical sequences allowed")
            if rule["name"] == "numericSequenceDeclined":
                human_password_rules.append("No numeric sequences allowed")
            if rule["name"] == "keyboardSequenceDeclined":
                human_password_rules.append("No keyboard sequences allowed")
            if rule["name"] == "blacklistedCharactersDeclined":
                human_password_rules.append("No blacklisted characters allowed")
            if rule["name"] == "repeatedCharactersDeclined":
                human_password_rules.append("No repeated characters allowed")
            if rule["name"] == "dictionaryWordsDeclined":
                human_password_rules.append("No dictionary words allowed")
        return human_password_rules

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

    def validate_password(self, password: str) -> dict:
        path = self.api_path("password")
        logger.info(f"Validating password for from {path}")
        r = self._request(
            "POST",
            path,
            verify=self.ssl_verify,
            headers=self.header.extra_header({"Content-Type": "application/json"}),
            json={"password": password},
        )
        return r

    def is_valid_password(self, password: str) -> bool:
        return self.validate_password(password).get("valid", False)

    def get_password(self) -> str:
        path = self.api_path("password")
        logger.info(f"Getting generated password from {path}")
        r = self._request(
            "GET",
            path,
            verify=self.ssl_verify,
            headers=self.header.request_header,
        )
        return r.get("password", None)

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
        p = CryptshareTransferPolicy(r)
        return p

    def download_transfer(self, transfer_id, password) -> CryptshareDownload:
        logger.debug(f"Downloading transfer {transfer_id} from {self._server}")
        return CryptshareDownload(self, transfer_id, password)

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
                status = {"trackingID": tracking_id, "status": transfer["status"]}
                transfer_status_list.append(status)
            return transfer_status_list

        logger.debug(f"Transfer status for transfer {transfer_tracking_id}\n")
        transfer = CryptshareTransfer(CryptshareTransferSettings(self._sender), tracking_id=transfer_tracking_id)
        transfer_status = transfer.get_transfer_status(self)
        return transfer_status

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
