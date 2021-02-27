from typing import Optional

from fastapi import FastAPI, Header, Depends
from fastapi.exceptions import HTTPException

from api.config import get_config, Config
from api.model import Provider
from api.providers.slack import slack_message, SlackMessage
from api.providers.discord import discord_message, DiscordMessage
from api.providers.twilio import twilio_message, TwilioMessage
from api.providers.sns import sns_message, SnsMessage
from api.dependencies import authorize, message


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


@api.get("/sns")
def sns(message: SnsMessage = Depends(sns_message)):
    message.send()
    return f"Sent '{message.message}' to SNS"


@api.get("/topic/{topic_name}")
def topic(
    topic_name: str,
    config: Config = Depends(get_config),
    message=Depends(message),
):
    topic = config.topic(topic_name)
    if not topic:
        raise HTTPException(
            status_code=501, detail=f"No topic '{topic_name}' configured"
        )
    for provider, params in topic.params(message):
        if provider == Provider.SLACK:
            SlackMessage(**params, config=config).send()
        elif provider == Provider.DISCORD:
            DiscordMessage(**params, config=config).send()
        elif provider == Provider.TWILIO:
            TwilioMessage(**params, config=config).send()
        elif provider == Provider.SNS:
            SnsMessage(**params, config=config).send()
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported provider '{provider}'"
            )
    return f"Sent {message} to topic '{topic_name}'"
