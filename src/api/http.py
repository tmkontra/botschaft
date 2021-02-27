import requests


class Request:
    def __init__(self, url, headers=None, body=None):
        self.url = url
        self.headers = headers
        self.body = body

    def get(self):
        resp = requests.get(self.url, headers=self.headers)
        print(f"GET {self.url} returned {resp.status_code}")
        resp.raise_for_status()
        return resp

    def post(self):
        resp = requests.post(self.url, json=self.body, headers=self.headers)
        print(f"POST {self.url} returned {resp.status_code}")
        resp.raise_for_status()
        return resp
