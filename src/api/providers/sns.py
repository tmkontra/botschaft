from typing import Optional
from fastapi import HTTPException, Depends
import boto3
from api.config import Config, get_config


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


def sns_message(
    message: Optional[str] = None,
    base64_message: Optional[str] = None,
    _sns=Depends(can_sns),
    config=Depends(get_config),
):
    if message:
        return SnsMessage(message, config)
    elif base64_message:
        message = base64.b64decode(base64_message).decode("utf-8")
        return SnsMessage(message, config)
    else:
        raise HTTPException(
            status_code=422, detail="Must provide one of 'message', 'base64_message'"
        )
