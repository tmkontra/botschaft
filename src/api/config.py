from os import getenv
from marshmallow import Schema, fields, post_load
import json

from twilio.rest import Client

_env_prefix = "BOTSCHAFT__"


def get_environment_variable(name: str, required=False):
    var_name = f"{_env_prefix}__{name}"
    var = getenv(var_name)
    if required and not var:
        raise ValueError(f"Required environment variable '{var_name}' is not set!")
    else:
        return var


class SlackConfigSchema(Schema):
    channels = fields.Mapping(keys=fields.String, values=fields.Url, required=True)


class DiscordConfigSchema(Schema):
    channels = fields.Mapping(keys=fields.String, values=fields.Url, required=True)


class TwilioConfigSchema(Schema):
    account_sid = fields.String(required=True)
    auth_token = fields.String(required=True)
    messaging_service_sid = fields.String(required=False)
    from_phone_number = fields.String(required=False)


class BotschaftConfigSchema(Schema):
    slack = fields.Nested(SlackConfigSchema, required=False)
    discord = fields.Nested(DiscordConfigSchema, required=False)
    twilio = fields.Nested(TwilioConfigSchema, required=False)

    @post_load
    def make_config(self, data, **kwargs):
        return Config(**data)


class Config:
    def __init__(self, **data):
        self.ACCESS_TOKEN = get_environment_variable("ACCESS_TOKEN")
        self.discord = data.get("discord", {})
        self.slack = data.get("slack", {})
        twilio = data.get("twilio")
        if twilio:
            client = Client(twilio["account_sid"], twilio["auth_token"])
            self.twilio = client
            self.twilio_from_parameter = self.twilio_from_parameter(twilio)
        else:
            self.twilio = None
            self.twilio_from_parameter = {}

    def discord_channel(self, name):
        return self.discord.get("channels", {}).get(name)

    def slack_channel(self, name):
        return self.slack.get("channels", {}).get(name)

    @staticmethod
    def twilio_from_parameter(twilio_config):
        if twilio_config.get("messaging_service_sid"):
            return dict(messaging_service_sid=twilio_config["messaging_service_sid"])
        elif twilio_config.get("from_phone_number"):
            return dict(from_=twilio_config["from_phone_number"])
        else:
            raise ValueError(
                "One of 'twilio.message_service_sid' or 'twilio.from_phone_number' must be provided!"
            )


def load_config():
    with open("botschaft.json", "r") as f:
        conf = json.load(f)
        schema = BotschaftConfigSchema()
        config = schema.load(conf)
        return config


_config = load_config()


def get_config():
    return _config
