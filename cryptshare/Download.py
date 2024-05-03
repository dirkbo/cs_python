import requests

from cryptshare.ApiRequestHandler import ApiRequestHandler


class Download(ApiRequestHandler):
    def __init__(self, url, header, transfer_id, password, ssl_verify=True):
        self.url = url
        self.ssl_verify = ssl_verify
        self.header = header
        self.transfer_id = transfer_id
        self.password = password

    def download_transfer_information(self):
        r = self._handle_response(
            requests.get(
                self.url + "/transfers/" + self.transfer_id + "?password=" + self.password,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def download_zip(self):
        r = self._handle_response(
            requests.get(
                self.url + "/transfers/" + self.transfer_id + "/zip?password=" + self.password,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def download_eml(self):
        r = self._handle_response(
            requests.get(
                self.url + "/transfers/" + self.transfer_id + "/eml?password=" + self.password,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r

    def download_files_info(self):
        r = self._handle_response(
            requests.get(
                self.url + "/transfers/" + self.transfer_id + "/files?password=" + self.password,
                verify=self.ssl_verify,
                headers=self.header.general,
            )
        )
        return r
