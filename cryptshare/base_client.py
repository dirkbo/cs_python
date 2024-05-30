import hashlib
import json
import logging
import os

from cryptshare.api_requests import CryptshareApiRequests
from cryptshare.header import CryptshareHeader
from cryptshare.validators import CryptshareValidators

logger = logging.getLogger(__name__)

CURRENT_MAXIMUM_TARGET_API_VERSION = "1.9"


class CryptshareBaseClient(CryptshareApiRequests):
    _target_api_version = CURRENT_MAXIMUM_TARGET_API_VERSION
    header: CryptshareHeader = None
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

    def set_verification_in_store(self, email: str, verification_token: str):
        hashed_email = hashlib.shake_256(email.encode("utf-8")).hexdigest(16)
        logger.debug(f"Setting verification token for {email} in client store")
        self._client_store.update({hashed_email: verification_token})

    def get_verification_from_store(self, email: str = None):
        hashed_email = hashlib.shake_256(email.encode("utf-8")).hexdigest(16)
        if hashed_email in self._client_store:
            logger.debug(f"Verification token for {email} found in client store")
            return self._client_store.get(hashed_email)
        logger.debug(f"No Verification token for {email} found in client store")
        return ""

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
