from typing import Optional
from fastapi import Depends, HTTPException
from .config import get_config, Config
import base64


class SlackMessage:
    def __init__(self, channel, message):
        self.channel = channel
        self.message = message

    def send(self):
        print(f"Sending slack message '{self.message}' to #{self.channel}")


def can_slack(config: Config = Depends(get_config)):
    if config.SLACK_API_KEY:
        return True
    else:
        raise HTTPException(status_code=501, detail="Slack API not configured")


def slack_message(
    channel: str,
    message: Optional[str] = None,
    base64_message: Optional[str] = None,
    _slack=Depends(can_slack),
):
    if message:
        return SlackMessage(channel, message)
    elif base64_message:
        message = base64.b64decode(base64_message).decode("utf-8")
        return SlackMessage(channel, message)
    else:
        raise HTTPException(
            status_code=422, detail="Must provide one of 'message', 'base64_message'"
        )
