from typing import Optional

import boto3
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from fastapi_utils.api_model import APIModel

from api.config import Config, get_config
from api.dependencies import message
from api.schemas import MessageRequest


class SnsMessageRequest(MessageRequest):
    pass


class SnsMessage:
    def __init__(self, message, config: Config):
        self.message = message
        self.config = config

    def send(self):
        client = self.config.boto.client("sns")
        try:
            client.publish(Message=self.message, TopicArn=self.config.sns_topic_arn)
        except boto3.exceptions.Boto3Error:
            raise HTTPException(status_code=500, detail="Failed to send SNS message")


def can_sns(config: Config = Depends(get_config)):
    if config.sns_topic_arn:
        return True
    else:
        raise HTTPException(status_code=501, detail="SNS Topic not configured")


sns_router = APIRouter()


@cbv(sns_router)
class SnsAPI:
    _sns = Depends(can_sns)
    config = Depends(get_config)

    @sns_router.get("/sns")
    def sns_get(self, message=Depends(message)):
        message = SnsMessage(message, self.config)
        message.send()
        return f"Sent '{message.message}' to SNS"

    @sns_router.post("/sns")
    def sns_post(self, request: SnsMessageRequest):
        try:
            SnsMessage(request.get_message(), self.config)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=e)
