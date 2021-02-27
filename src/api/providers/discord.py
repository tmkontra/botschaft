import base64
from typing import Optional

from fastapi import Depends, HTTPException

from api.config import get_config, Config
from api.http import Request


class DiscordMessage:
    def __init__(self, channel, message, config: Config):
        self.channel = channel
        self.message = message
        self.config = config

    def send(self):
        body = {"content": self.message}
        url = self.config.discord_channel(self.channel)
        if not url:
            raise HTTPException(
                status_code=501,
                detail=f"Discord channel '{self.channel}' not configured",
            )
        g = Request(url, body=body)
        print(f"Sending discord message '{self.message}' to #{self.channel}")
        try:
            resp = g.post()
            return True
        except:
            raise HTTPException(status_code=500)


def can_discord(config: Config = Depends(get_config)):
    if config.discord:
        return True
    else:
        raise HTTPException(status_code=501, detail="Discord API not configured")


def discord_message(
    channel: str,
    message: Optional[str] = None,
    base64_message: Optional[str] = None,
    _discord=Depends(can_discord),
    config=Depends(get_config),
):
    if message:
        return DiscordMessage(channel, message, config)
    elif base64_message:
        message = base64.b64decode(base64_message).decode("utf-8")
        return DiscordMessage(channel, message, config)
    else:
        raise HTTPException(
            status_code=422, detail="Must provide one of 'message', 'base64_message'"
        )
