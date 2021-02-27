import base64
from typing import Optional
from fastapi import Depends, HTTPException
from twilio.rest import Client

from api.config import Config, get_config


class TwilioMessage:
    def __init__(self, to_phone_number: str, message: str, config: Config):
        self.to = to_phone_number
        self.message = message
        self.config = config

    def send(self):
        client: Client = self.config.twilio
        try:
            resp = client.messages.create(
                to=self.to, body=self.message, **self.config.twilio_from_parameter
            )
            if resp.error_code:
                print(
                    f"Twilio failed to send message '{self.message}' to '{self.to}', error_code={resp.error_code} error_message={resp.error_message}"
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Twilio SMS failed with error code {resp.error_code}",
                )
            else:
                print(f"Twilio sent message sid {resp.sid}")
                return True
        except Exception as e:
            print(f"Twilio API failure: {e}")
            raise HTTPException(status_code=500, detail="Twilio API failure")


def can_twilio(config: Config = Depends(get_config)):
    if config.twilio:
        return True
    else:
        raise HTTPException(status_code=501, detail="Twilio API not configured")


def twilio_message(
    to: str,
    message: Optional[str] = None,
    base64_message: Optional[str] = None,
    _twilio=Depends(can_twilio),
    config=Depends(get_config),
):
    if message:
        return TwilioMessage(to, message, config)
    elif base64_message:
        message = base64.b64decode(base64_message).decode("utf-8")
        return TwilioMessage(to, message, config)
    else:
        raise HTTPException(
            status_code=422, detail="Must provide one of 'message', 'base64_message'"
        )
