import pytest
import requests

from api.config import Config
from api.providers import sns

from . import aws_config


test_config = aws_config({"sns": {"topic_arn": "fake-arn"}})


def test_sns_message():
    sns_message = sns.SnsMessage(message="test message", config=test_config)
    sns_message.send()
    assert True
