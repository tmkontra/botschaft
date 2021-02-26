from os import getenv
from marshmallow import Schema, fields, post_load
import json


_env_prefix = "BOTSCHAFT__"


def get_environment_variable(name: str, required=False):
    var_name = f"{_env_prefix}__{name}"
    var = getenv(var_name)
    if required and not var:
        raise ValueError(f"Required environment variable '{var_name}' is not set!")
    else:
        return var


class SlackConfigSchema(Schema):
    channels = fields.Mapping(keys=fields.String, values=fields.Url)


class DiscordConfigSchema(Schema):
    channels = fields.Mapping(keys=fields.String, values=fields.Url)


class BotschaftConfigSchema(Schema):
    slack = fields.Nested(SlackConfigSchema)
    discord = fields.Nested(DiscordConfigSchema)

    @post_load
    def make_config(self, data, **kwargs):
        return Config(**data)


class Config:
    def __init__(self, **data):
        self.ACCESS_TOKEN = get_environment_variable("ACCESS_TOKEN")
        self.discord = data.get("discord", {})
        self.slack = data.get("slack", {})

    def discord_channel(self, name):
        return self.discord.get("channels", {}).get(name)

    def slack_channel(self, name):
        return self.slack.get("channels", {}).get(name)


def load_config():
    with open("botschaft.json", "r") as f:
        conf = json.load(f)
        schema = BotschaftConfigSchema()
        config = schema.load(conf)
        return config


_config = load_config()


def get_config():
    return _config
