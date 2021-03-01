import requests

from api import config
from api.config import Config
from api.http import HTTPRequest


class MockRequests:
    class MockResponse:
        def __init__(self, status_code: int, *args, **kwargs):
            self.status_code = status_code
            self._args = args
            self._kwargs = kwargs

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(
                    f"MockResponse has status_code {self.status_code}"
                )

    def __init__(self):
        self.requests = []

    def get(self, *args, **kwargs):
        self.requests.append((args, kwargs))
        return self.MockResponse(200)

    def post(self, *args, **kwargs):
        self.requests.append((args, kwargs))
        return self.MockResponse(200)


HTTPRequest.api = MockRequests()

import boto3
from botocore.stub import Stubber


class MockBoto:
    def __init__(self):
        self.clients = {}

    def client(self, name):
        client = boto3.client(name)
        self.clients[name] = client
        stubber = Stubber(client)
        self._stub(stubber, name)
        stubber.activate()
        return client

    def _stub(self, stub: Stubber, name):
        if name == "sns":
            stub.add_response("publish", {"MessageId": "ok"})
        else:
            return


def aws_config(providers: dict):
    test = config.TEST_CONFIG
    config.TEST_CONFIG = True
    cfg = Config(
        providers={
            "aws": dict(
                access_key_id="access",
                secret_access_key="secret",
                region="region",
                **providers,
            )
        },
        topics=[],
        boto=MockBoto(),
    )
    config.TEST_CONFIG = test
    return cfg
