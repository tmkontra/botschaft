from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from fastapi_utils.api_model import APIModel
from pydantic import BaseModel
from twilio.rest import Client

from api.config import Config, get_config
from api.dependencies import message
from api.logger import get_logger
from api.schemas import MessageRequest

logger = get_logger(__name__)


class TwilioMessageRequest(MessageRequest):
    to: str


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
                logger.error(
                    f"Twilio failed to send message '{self.message}' to '{self.to}', error_code={resp.error_code} error_message={resp.error_message}"
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Twilio SMS failed with error code {resp.error_code}",
                )
            else:
                logger.debug(f"Twilio sent message sid {resp.sid}")
                return True
        except Exception as e:
            logger.exception(f"Twilio API failure")
            raise HTTPException(status_code=500, detail="Twilio API failure")


def can_twilio(config: Config = Depends(get_config)):
    if config.twilio:
        return True
    else:
        raise HTTPException(status_code=501, detail="Twilio API not configured")


twilio_router = APIRouter()


@cbv(twilio_router)
class TwilioAPI:
    _twilio = Depends(can_twilio)
    config: Config = Depends(get_config)

    @twilio_router.get("/twilio")
    def twilio_message_get(self, to: str, message=Depends(message)):
        sms = TwilioMessage(to, message, self.config)
        sms.send()
        return f"Sent '{message}' to '{to}'"

    @twilio_router.post("/twilio")
    def twilio_message_post(self, request: TwilioMessageRequest):
        try:
            sms = TwilioMessage(request.to, request.get_message(), self.config)
            sms.send()
        except ValueError as e:
            raise HTTPException(status_code=422, detail=e)
