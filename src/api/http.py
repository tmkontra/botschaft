import requests

from api.logger import get_logger

logger = get_logger(__name__)


class Request:
    def __init__(self, url, headers=None, body=None):
        self.url = url
        self.headers = headers
        self.body = body

    def get(self):
        resp = requests.get(self.url, headers=self.headers)
        logger.debug(f"GET {self.url} returned {resp.status_code}")
        resp.raise_for_status()
        return resp

    def post(self):
        resp = requests.post(self.url, json=self.body, headers=self.headers)
        logger.debug(f"POST {self.url} returned {resp.status_code}")
        resp.raise_for_status()
        return resp
