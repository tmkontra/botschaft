from typing import Optional

from fastapi import FastAPI, Header, Depends
from fastapi.exceptions import HTTPException

from api.config import get_config, Config
from api.providers.slack import slack_message, SlackMessage
from api.providers.discord import discord_message, DiscordMessage
from api.providers.twilio import twilio_message, TwilioMessage
from api.dependencies import authorize

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


@api.get("/twilio")
def twilio(message: TwilioMessage = Depends(twilio_message)):
    message.send()
    return f"Sent '{message.message}' to '{message.to}'"
