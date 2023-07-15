import requests

from api.logger import get_logger

logger = get_logger(__name__)


class HTTPRequest:
    api = requests

    def __init__(self, url, headers=None, body=None):
        self.url = url
        self.headers = headers
        self.body = body

    def get(self):
        logger.debug(f"Making request to GET {self.url}")
        resp = self.api.get(self.url, headers=self.headers)
        logger.debug(f"GET {self.url} returned {resp.status_code}")
        resp.raise_for_status()
        return resp

    def post(self):
        logger.debug(f"Making request to POST {self.url} with body {self.body}")
        resp = self.api.post(self.url, json=self.body, headers=self.headers)
        logger.debug(f"POST {self.url} returned {resp.status_code}")
        resp.raise_for_status()
        return resp
