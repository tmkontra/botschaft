from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from api.config import get_config, Config
from api.dependencies import message
from api.http import Request
from api.logger import get_logger
from api.schemas import MessageRequest


logger = get_logger(__name__)


class SlackMessageRequest(MessageRequest):
    channel: str


class SlackMessage:
    def __init__(self, channel, message, config: Config):
        self.channel = channel
        channel_url = config.slack_channel(channel)
        if not channel_url:
            raise HTTPException(
                status_code=501, detail=f"No slack channel '{channel}' configured"
            )
        self.channel_url = channel_url
        self.message = message

    def send(self):
        body = {"text": self.message}
        g = Request(self.channel_url, body=body)
        logger.debug(f"Sending slack message '{self.message}' to #{self.channel}")
        try:
            resp = g.post()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Unable to send slack message: %s" % e
            )


def can_slack(config: Config = Depends(get_config)):
    if config.slack:
        return True
    else:
        raise HTTPException(status_code=501, detail="Slack API not configured")


slack_router = APIRouter()


@cbv(slack_router)
class SlackAPI:
    _slack = Depends(can_slack)
    config: Config = Depends(get_config)

    @slack_router.get("/slack")
    def slack_get(self, channel: str, message=Depends(message)):
        slack = SlackMessage(channel, message, self.config)
        slack.send()
        return f"Sent '{message}' to '{channel}'"

    @slack_router.post("/slack")
    def slack_post(self, request: SlackMessageRequest):
        slack = SlackMessage(request.channel, request.get_message(), self.config)
        slack.send()
        return f"Sent '{slack.message}' to '{slack.channel}'"
