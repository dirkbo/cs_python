import json
import logging

import requests

import cryptshare.Download as Download
import cryptshare.Header as CryptshareHeader
import cryptshare.Transfer as Transfer
import cryptshare.TransferSettings as TransferSettings
from cryptshare.ApiRequestHandler import ApiRequestHandler

logger = logging.getLogger(__name__)


class Client(ApiRequestHandler):
    header = CryptshareHeader.Header()
    email_address = ""
    _server = ""
    api_path_users = "/users/"
    _api_paths = {
        "users": "/api/users/",
        "clients": "/api/users/clients",
        "products": "/api/users/products/",
        "password_requirements": "/api/password/requirements",
        "password": "/api/password",
    }
    store = {}

    def __init__(self, server, client_store_path="client_store.json", ssl_verify=True):
        logger.debug(f"Initialising Cryptshare Client for server: {server}")
        self._server = server
        self.client_store_path = client_store_path
        self.ssl_verify = ssl_verify

    @property
    def server(self):
        return self._server

    @server.setter
    def server(self, server: str):
        logger.debug(f"Setting server to {server}")
        self._server = server

    def api_path(self, path: str):
        return f"{self._server}{self._api_paths.get(path, '')}"

    def reset_headers(self):
        logger.debug("Resetting headers")
        self.header = CryptshareHeader.Header()

    def set_email(self, email: str):
        logger.debug(f"Setting Cryptshare Client email to {email}")
        self.email_address = email
        if self.email_address in self.store:
            logger.debug(f"Setting verification token for {email} from client store")
            verification = self.store.get(self.email_address)
            self.header.set_verification(verification)
        else:
            logger.debug(f"No verification token found for {email}, not setting verification token")
            self.header.set_verification("")

    def get_emails(self) -> list[str]:
        logger.debug("Getting emails from client store")
        return_list = []
        for a in self.store:
            if "@" in a:
                return_list.append(a)
        return return_list

    def delete_email(self, email: str):
        logger.debug(f"Deleting email {email} from client store")
        if email in self.store:
            self.store.remove(email)

    def request_code(self):
        path = self.api_path('users') + self.email_address + "/verification/code/email"
        logger.debug(f"Requesting verification code for {self.email_address} from {path}")
        self._handle_response(
            requests.post(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )

    def verify_code(self, code: str):
        url = f"{self.api_path('users')}{self.email_address}/verification/token"
        logger.debug(f"Verifying code {code} for {self.email_address} from {url} to obtain verification token")
        r = self._handle_response(
            requests.post(
                url,
                json={"verificationCode": code},
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        verification_token = r.get("token")
        logger.debug(f"Storing verification token for {self.email_address} in client store")
        self.store.update({self.email_address: verification_token})
        logger.debug(f"Setting verification token for {self.email_address} in client headers")
        self.header.set_verification(verification_token)
        return True

    def is_verified(self):
        path = f"{self.api_path('users')}{self.email_address}/verification"
        logger.debug(f"Checking if {self.email_address} is verified from {path}")
        # ToDO: Fix problem when cors header is present
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r.get("verified")

    def get_verification(self):
        path = f"{self.api_path('users')}{self.email_address}/verification"
        logger.debug(f"Getting verification status for {self.email_address} from {path}")
        # ToDO: Fix problem when cors header is present
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def cors(self, origin: str):
        path = f"{self.api_path('products')}api.rest/cors"
        logger.debug(f"Checking CORS for origin {origin} and {path}")
        self.header.set_origin(origin)

        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        logger.info(f"CORS is active for origin {origin}: {r.get('active')}")

    def exists_client_id(self) -> bool:
        logger.debug("Checking if client ID exists in Headers")
        if "X-CS-ClientId" in self.header.general:
            return True
        return False

    def start_transfer(self, recipients, settings: TransferSettings.TransferSettings):
        logger.debug(f"Starting transfer for {self.email_address} to {recipients} with settings {settings}")
        transfer = Transfer.Transfer(
            self.header.general,
            recipients.get("to"),
            recipients.get("cc"),
            recipients.get("bcc"),
            settings,
            ssl_verify=self.ssl_verify,
        )
        path = f"{self.api_path('users')}{self.email_address}/transfer-sessions"
        logger.debug(f"Starting transfer for {self.email_address} from {path}")
        r = self._handle_response(
            requests.post(
                path,
                verify=self.ssl_verify,
                headers=self.header.other_header({"Content-Type": "application/json"}),
                json=transfer.get_data(),
            )
        )
        transfer.set_location(r)
        transfer.edit_transfer_settings(settings)
        return transfer

    def request_client_id(self):
        path = self.api_path('clients')
        logger.debug(f"Requesting client ID from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        logger.debug("Storing client ID in client store")
        self.header.set_client_id(r.get("clientId"))
        logger.debug("Setting client ID in client headers")
        self.store.update({"X-CS-ClientId": r.get("clientId")})

    def read_client_store(self):
        logger.debug(f"Reading client store from {self.client_store_path}")
        try:
            with open(self.client_store_path, "r") as json_file:
                try:
                    self.store = json.load(json_file)
                except Exception as e:
                    print(f"Failed to read store: {e}")
            if "X-CS-ClientId" in self.store:
                self.header.set_client_id(self.store.get("X-CS-ClientId"))
        except IOError:
            logger.warning(f"Failed to read client store from {self.client_store_path}")
            return ""

    def write_client_store(self):
        logger.debug(f"Writing client store to {self.client_store_path}")
        try:
            with open(self.client_store_path, "w") as outfile:
                json.dump(self.store, outfile, indent=4)
            outfile.close()
        except IOError:
            logger.warning(f"Failed to write client store to {self.client_store_path}")

    def get_password_rules(self):
        path =self.api_path('password_requirements')
        logger.debug(f"Getting password rules from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def get_transfers(self):
        path = self.api_path('users') + self.email_address + "/transfers"
        logger.debug(f"Getting transfers for {self.email_address} from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def validate_password(self, password):
        path = self.api_path('password')
        logger.debug(f"Validating password for {self.email_address} from {path}")
        r = self._handle_response(
            requests.post(
                path,
                verify=self.ssl_verify,
                headers=self.header.other_header({"Content-Type": "application/json"}),
                json={"password": password},
            )
        )
        return r

    def get_password(self):
        path = self.api_path('password')
        logger.debug(f"Getting generated password from {path}")
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def get_policy(self, recipients):
        path = self.api_path('users') + self.email_address + "/transfer-policy"
        logger.debug(f"Getting policy for {self.email_address} and  {recipients} from {path}")
        r = self._handle_response(
            requests.post(
                path,
                verify=self.ssl_verify,
                headers=self.header.other_header({"Content-Type": "application/json"}),
                json={"recipients": recipients},
            )
        )
        return r

    def download(self, transfer_id, password) -> Download:
        logger.debug(f"Downloading transfer {transfer_id} from {self._server}")
        return Download.Download(self.api_path("users"), self.header, transfer_id, password, ssl_verify=self.ssl_verify)
