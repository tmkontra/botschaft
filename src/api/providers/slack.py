import base64
from typing import Optional

from fastapi import Depends, HTTPException

from api.config import get_config, Config
from api.dependencies import message
from api.http import Request


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
        print(f"Sending slack message '{self.message}' to #{self.channel}")
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


def slack_message(
    channel: str,
    message=Depends(message),
    _slack=Depends(can_slack),
    config=Depends(get_config),
):
    return SlackMessage(channel, message, config)
