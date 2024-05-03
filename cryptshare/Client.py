import json
import sys

import requests

import cryptshare.Download as Download
import cryptshare.Header as CryptshareHeader
import cryptshare.Transfer as Transfer
import cryptshare.TransferSettings as TransferSettings
from cryptshare.ApiRequestHandler import ApiRequestHandler


class Client(ApiRequestHandler):
    header = CryptshareHeader.Header()
    email_address = ""
    url = ""
    path1 = "/users/"
    store = {}

    def __init__(self, server, client_store_path="client_store.json", ssl_verify=True):
        self.url = server + "/api"
        self.client_store_path = client_store_path
        self.ssl_verify = ssl_verify

    def set_url(self, server: str):
        self.url = server + "/api"

    def reset_headers(self):
        self.header = CryptshareHeader.Header()

    def set_email(self, email: str):
        self.email_address = email
        if self.email_address in self.store:
            verification = self.store.get(self.email_address)
            self.header.set_verification(verification)
        else:
            self.header.set_verification("")

    def get_emails(self) -> list[str]:
        return_list = []
        for a in self.store:
            if "@" in a:
                return_list.append(a)
        return return_list

    def delete_email(self, email: str):
        if email in self.store:
            self.store.remove(email)

    def request_code(self):
        self._handle_response(
            requests.post(
                self.url + self.path1 + self.email_address + "/verification/code/email",
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )

    def verify_code(self, code: str):
        r = self._handle_response(
            requests.post(
                self.url + self.path1 + self.email_address + "/verification/token",
                json={"verificationCode": code},
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        verification_token = r.get("token")
        self.store.update({self.email_address: verification_token})
        self.header.set_verification(verification_token)
        return True

    def is_verified(self):
        path = self.url + self.path1 + self.email_address + "/verification"
        #print(f"{path} - {self.ssl_verify} - {self.header.general}")
        # ToDO: Fix problem when cors header is present
        r = self._handle_response(
            requests.get(
                path,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r.get("verified")

    def cors(self, origin: str):
        self.header.set_origin(origin)
        r = self._handle_response(
            requests.get(
                self.url + "/products/" + "api.rest/cors",
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        print(f"CORS is active for origin {origin}: {r.get('active')}")

    def exists_client_id(self) -> bool:
        if "X-CS-ClientId" in self.header.general:
            return True
        return False

    def start_transfer(self, recipients, settings: TransferSettings.TransferSettings):
        transfer = Transfer.Transfer(
            self.header.general,
            recipients.get("to"),
            recipients.get("cc"),
            recipients.get("bcc"),
            settings,
            ssl_verify=self.ssl_verify,
        )
        r = self._handle_response(
            requests.post(
                self.url + self.path1 + self.email_address + "/transfer-sessions",
                verify=self.ssl_verify,
                headers=self.header.other_header({"Content-Type": "application/json"}),
                json=transfer.get_data(),
            )
        )
        transfer.set_location(r)
        transfer.edit_transfer_settings(settings)
        return transfer

    def request_client_id(self):
        r = self._handle_response(
            requests.get(
                self.url + "/clients",
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        self.header.set_client_id(r.get("clientId"))
        self.store.update({"X-CS-ClientId": r.get("clientId")})

    def read_client_store(self):
        try:
            with open(self.client_store_path, "r") as json_file:
                try:
                    self.store = json.load(json_file)
                except Exception as e:
                    print(f"Failed to read store: {e}")
            if "X-CS-ClientId" in self.store:
                self.header.set_client_id(self.store.get("X-CS-ClientId"))
        except IOError:
            return ""

    def write_client_store(self):
        with open(self.client_store_path, "w") as outfile:
            json.dump(self.store, outfile, indent=4)
        outfile.close()

    def get_password_rules(self):
        r = self._handle_response(
            requests.get(
                self.url + "/password/requirements",
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def validate_password(self, password):
        r = self._handle_response(
            requests.post(
                self.url + "/password",
                verify=self.ssl_verify,
                headers=self.header.other_header({"Content-Type": "application/json"}),
                json={"password": password},
            )
        )
        return r

    def get_password(self):
        r = self._handle_response(
            requests.get(
                self.url + "/password",
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def get_policy(self, recipients):
        r = self._handle_response(
            requests.post(
                self.url + self.path1 + self.email_address + "/transfer-policy",
                verify=self.ssl_verify,
                headers=self.header.other_header({"Content-Type": "application/json"}),
                json={"recipients": recipients},
            )
        )
        return r

    def download(self, transfer_id, password) -> Download:
        return Download.Download(self.url, self.header, transfer_id, password, ssl_verify=self.ssl_verify)
