import pytest
import requests

from api.config import Config
from api.providers import discord


test_config = Config(
    providers={"discord": {"channels": {"alerts": "fake-webhook"}}}, topics=[]
)


def test_discord_message():
    discord_message = discord.DiscordMessage(
        channel="alerts", message="test message", config=test_config
    )
    discord_message.send()
    assert True
