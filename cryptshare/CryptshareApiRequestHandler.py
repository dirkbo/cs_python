import json
import logging

from requests import HTTPError

logger = logging.getLogger(__name__)


class CryptshareApiRequestHandler:
    @staticmethod
    def _handle_response(resp):
        logger.debug(f"Handling API response\n {resp.status_code}\n {resp.headers}\n {resp.content}\n")
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
                logger.warning("403 Error: 3001")
                err_msg = f"403 Error \n{content.get('errorCode')}\n{content.get('errorMessage')}\nPlease install a valid Cryptshare license on this Cryptshare server where the REST API is licensed."
                raise HTTPError(err_msg)
            logger.warning(f"403 Error: {content.get('errorCode')} - {content.get('errorMessage')}")
            err_msg = f"403 Error \n{content.get('errorCode')}\n{content.get('errorMessage')}"
            raise HTTPError(err_msg)
        if resp.status_code in [400, 401, 404, 406, 409, 410, 429, 500, 501]:
            logger.warning(f"{resp.status_code} Error")
            content = json.loads(resp.content)
            err_msg = f"{resp.status_code} Error \n{content.get('errorCode')}\n{content.get('errorMessage')}"
            raise HTTPError(err_msg)
