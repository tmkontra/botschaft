from typing import Optional

from fastapi import FastAPI, Header, Depends
from fastapi.exceptions import HTTPException

from .config import get_config, Config
from .slack import slack_message, SlackMessage
from .discord import discord_message, DiscordMessage
from .dependencies import authorize

api = FastAPI(
    dependencies=[
        Depends(authorize),
    ]
)


@api.get("/slack")
def slack(message: SlackMessage = Depends(slack_message)):
    message.send()
    return f"Sent '{message.message}' to #{message.channel}"


@api.get("/discord")
def discord(message: DiscordMessage = Depends(discord_message)):
    message.send()
    return f"Sent '{message.message}' to #{message.channel}"
