import pytest

from api.config import Config
from api.providers import twilio


class MockTwilioClient:
    class TwilioMessages:
        class FakeTwilioMessage:
            def __init__(self):
                import uuid

                self.error_code = None
                self.sid = uuid.uuid4()

        def __init__(self):
            self.sent_messages = []

        def create(self, to: str, body: str, *args, **from_parameter):
            message = self.FakeTwilioMessage()
            self.sent_messages.append(message)
            return message

    def __init__(self):
        self.messages = self.TwilioMessages()


test_config = Config(
    providers={
        "twilio": {
            "account_sid": "fake_sid",
            "auth_token": "fake_token",
            "messaging_service_sid": "fake_sid",
        }
    },
    topics=[],
)
twilio_client = MockTwilioClient()
test_config.twilio = twilio_client


def test_twilio_message():
    twilio_message = twilio.TwilioMessage(
        to_phone_number="4847443806", message="test message", config=test_config
    )
    twilio_message.send()
    assert True
