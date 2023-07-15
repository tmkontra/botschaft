import pytest
import requests

from api.config import Config
from api.providers import slack


test_config = Config(
    providers={"slack": {"channels": {"alerts": "fake-webhook"}}}, topics=[]
)


def test_slack_message():
    slack_message = slack.SlackMessage(
        channel="alerts", message="test message", config=test_config
    )
    slack_message.send()
    assert True
