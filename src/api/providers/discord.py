from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from api.config import get_config, Config
from api.dependencies import message
from api.http import Request
from api.logger import get_logger
from api.model import Provider
from api.schemas import MessageRequest
from .message import Message


logger = get_logger(__name__)


class DiscordMessageRequest(MessageRequest):
    channel: str


class DiscordMessage(Message):
    provider = Provider.DISCORD

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
        self.log_message(self.message, self.channel)
        try:
            resp = g.post()
            self.log_sent(self.message, self.channel)
            return True
        except:
            raise HTTPException(status_code=500)


def can_discord(config: Config = Depends(get_config)):
    if config.discord:
        return True
    else:
        raise HTTPException(status_code=501, detail="Discord API not configured")


discord_router = APIRouter()


@cbv(discord_router)
class DiscordAPI:
    _discord = Depends(can_discord)
    config: Config = Depends(get_config)

    @discord_router.get("/discord")
    def discord_get(self, channel: str, message: str = Depends(message)):
        discord = DiscordMessage(channel, message, self.config)
        discord.send()
        return f"Sent '{discord.message}' to #{discord.channel}"

    @discord_router.post("/discord")
    def discord_post(self, request: DiscordMessageRequest):
        discord = DiscordMessage(request.channel, request.message, self.config)
        discord.send()
        return f"Sent '{discord.message}' to #{discord.channel}"
