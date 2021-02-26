import base64
from typing import Optional

from fastapi import Depends, HTTPException

from .config import get_config, Config
from .gateway import Gateway


class SlackMessage:
    def __init__(self, channel, message, config):
        self.channel = channel
        self.message = message
        self.config = config

    def send(self):
        body = {"text": self.message}
        g = Gateway(self.config.SLACK_WEBHOOK_URL, body=body)
        print(f"Sending slack message '{self.message}' to #{self.channel}")
        try:
            resp = g.post()
        except:
            raise HTTPException(status_code=500)


def can_slack(config: Config = Depends(get_config)):
    if config.SLACK_WEBHOOK_URL:
        return True
    else:
        raise HTTPException(status_code=501, detail="Slack API not configured")


def slack_message(
    channel: str,
    message: Optional[str] = None,
    base64_message: Optional[str] = None,
    _slack=Depends(can_slack),
    config=Depends(get_config),
):
    if message:
        return SlackMessage(channel, message, config)
    elif base64_message:
        message = base64.b64decode(base64_message).decode("utf-8")
        return SlackMessage(channel, message, config)
    else:
        raise HTTPException(
            status_code=422, detail="Must provide one of 'message', 'base64_message'"
        )
