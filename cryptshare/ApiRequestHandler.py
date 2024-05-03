import json

from requests import HTTPError


class ApiRequestHandler(object):
    def _handle_response(self, resp):
        if resp.status_code == 200:  # or requests.code.ok
            if len(resp.content) == 0:
                return
            return json.loads(resp.content).get("data")
        if resp.status_code == 201:  # or requests.code.ok
            return resp.headers.get("Location")
        if resp.status_code == 204:  # or requests.code.ok
            return
        if resp.status_code == 403:
            content = json.loads(resp.content)
            if content.get("errorCode") == 3001:
                err_msg = f"403 Error \n{content.get('errorCode')}\n{content.get('errorMessage')}\nPlease install a valid Cryptshare license on this Cryptshare server where the REST API is licensed."
                raise HTTPError(err_msg)
            err_msg = f"403 Error \n{content.get('errorCode')}\n{content.get('errorMessage')}"
            raise HTTPError(err_msg)
        if resp.status_code in [400, 401, 404, 406, 409, 410, 429, 500, 501]:
            content = json.loads(resp.content)
            err_msg = f"{resp.status_code} Error \n{content.get('errorCode')}\n{content.get('errorMessage')}"
            raise HTTPError(err_msg)
