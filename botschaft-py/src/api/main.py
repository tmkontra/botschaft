from typing import Optional

from fastapi import FastAPI, Header, Depends
from fastapi.exceptions import HTTPException

from api.config import get_config, Config
from api.model import Provider
from api.providers.slack import slack_router
from api.providers.discord import discord_router
from api.providers.twilio import twilio_router
from api.providers.sns import sns_router
from api.dependencies import authorize, message
from api import schemas


api = FastAPI(
    dependencies=[
        Depends(authorize),
    ]
)


api.include_router(slack_router, tags=["slack"])
api.include_router(discord_router, tags=["discord"])
api.include_router(twilio_router, tags=["twilio"])
api.include_router(sns_router, tags=["sns"])


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


@api.get("/config", response_model=schemas.Config)
def config(config: Config = Depends(get_config)):
    return schemas.config_to_response(config)
