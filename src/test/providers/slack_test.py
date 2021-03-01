import pytest
import requests

from api.config import Config
from api.http import HTTPRequest
from api.providers import slack

test_config = Config(
    providers={"slack": {"channels": {"alerts": "fake-webhook"}}}, topics=[]
)


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


def test_slack_message():
    slack_message = slack.SlackMessage(
        channel="alerts", message="test message", config=test_config
    )
    slack_message.send()
    assert True
