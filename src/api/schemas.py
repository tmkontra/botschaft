import base64
from typing import Optional, List, Mapping

from fastapi import HTTPException
from pydantic import BaseModel

from api import config
from api.logger import get_logger
from api.model import Provider


logger = get_logger(__name__)


class Config(BaseModel):
    providers: Mapping
    topics: List


def config_to_response(config: config.Config):
    p = config.provider_info
    return Config(providers=config.provider_info, topics=list(config.topics.keys()))


class MessageRequest(BaseModel):
    message: Optional[str]
    base64_message: Optional[str]

    def get_message(self):
        if self.message:
            return self.message
        elif self.base64_message:
            try:
                msg = base64.b64decode(self.base64_message).decode("utf-8")
            except UnicodeDecodeError:
                logger.exception(
                    f"Could not parse base64_message '{self.base64_message}'"
                )
                raise HTTPException(
                    status_code=422, detail="Error parsing base64_message"
                )
        else:
            raise ValueError("Must provide one of 'message' or 'base64_message'")
