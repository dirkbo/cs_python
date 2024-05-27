import json
import logging

import requests

logger = logging.getLogger(__name__)


class CryptshareApiRequests:
    def _request(
        self,
        method,
        url,
        data=None,
        json=None,
        headers=None,
        verify=None,
        params=None,
        stream=False,
        handle_response=True,
        timeout: int =None,
    ):
        logger.info(f"Sending API request\n {method} {url}")
        logger.debug(f"\n Data: {data}\n Json: {json}\n Headers: {headers}\n Params: {params}")
        resp = requests.request(
            method, url, json=json, data=data, headers=headers, params=params, verify=verify, stream=stream, timeout=timeout
        )
        if stream or not handle_response:
            return resp
        return self._handle_response(resp)

    @staticmethod
    def _handle_response(resp):
        logger.info(f"\nResponse Status code: {resp.status_code}")
        logger.debug(f" Headers: {resp.headers}\n Content: {resp.content}\n")
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
                raise requests.HTTPError(err_msg)
            logger.warning(f"403 Error: {content.get('errorCode')} - {content.get('errorMessage')}")
            err_msg = f"403 Error \n{content.get('errorCode')}\n{content.get('errorMessage')}"
            raise requests.HTTPError(err_msg)
        if resp.status_code in [400, 401, 404, 406, 409, 410, 429, 500, 501]:
            logger.warning(f"{resp.status_code} Error")
            content = json.loads(resp.content)
            err_msg = f"{resp.status_code} Error \n{content.get('errorCode')}\n{content.get('errorMessage')}"
            raise requests.HTTPError(err_msg)
