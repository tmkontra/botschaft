import json
from os import getenv
from typing import Mapping

import boto3
from marshmallow import Schema, fields, post_load
from ruamel.yaml import YAML
import toml

from api.logger import get_logger
from api.model import Topic, Provider

from twilio.rest import Client

_env_prefix = "BOTSCHAFT__"

logger = get_logger(__name__)


def get_environment_variable(name: str, required=False):
    var_name = f"{_env_prefix}__{name}"
    var = getenv(var_name)
    if required and not var:
        raise ValueError(f"Required environment variable '{var_name}' is not set!")
    else:
        return var


class TopicConfigSchema(Schema):
    name = fields.String(required=True)
    destinations = fields.List(fields.String(required=True), required=True)


class SlackConfigSchema(Schema):
    channels = fields.Mapping(keys=fields.String, values=fields.Url, required=True)


class DiscordConfigSchema(Schema):
    channels = fields.Mapping(keys=fields.String, values=fields.Url, required=True)


class TwilioConfigSchema(Schema):
    account_sid = fields.String(required=True)
    auth_token = fields.String(required=True)
    messaging_service_sid = fields.String(required=False)
    from_phone_number = fields.String(required=False)


class SnsConfigSchema(Schema):
    topic_arn = fields.String(required=True)


class AwsConfigSchema(Schema):
    access_key_id = fields.String(required=False)
    secret_access_key = fields.String(required=False)
    region = fields.String(required=False)
    sns = fields.Nested(SnsConfigSchema, required=False)


class ProvidersConfigSchema(Schema):
    slack = fields.Nested(SlackConfigSchema, required=False)
    discord = fields.Nested(DiscordConfigSchema, required=False)
    twilio = fields.Nested(TwilioConfigSchema, required=False)
    aws = fields.Nested(AwsConfigSchema, required=False)


class BotschaftConfigSchema(Schema):
    providers = fields.Nested(ProvidersConfigSchema, required=True)
    topics = fields.List(fields.Nested(TopicConfigSchema), required=False)

    @post_load
    def make_config(self, data, **kwargs):
        return Config(providers=data.get("providers"), topics=data.get("topics"))


class Config:
    boto: boto3.Session

    def __init__(self, providers, topics):
        self.ACCESS_TOKEN = get_environment_variable("ACCESS_TOKEN")
        self.discord = providers.get("discord", {})
        self.slack = providers.get("slack", {})
        twilio = providers.get("twilio")
        if twilio:
            client = Client(twilio["account_sid"], twilio["auth_token"])
            self.twilio = client
            self.twilio_from_parameter = self.twilio_from_parameter(twilio)
        else:
            self.twilio = None
            self.twilio_from_parameter = {}
        aws = providers.get("aws", {})
        self.sns_topic_arn = aws.get("sns", {}).get("topic_arn")
        if topics:
            self.topics = self.load_topics(topics)
        else:
            self.topics = {}
        self.provider_info = self.providers_available(self)

    def discord_channel(self, name):
        return self.discord.get("channels", {}).get(name)

    def slack_channel(self, name):
        return self.slack.get("channels", {}).get(name)

    def topic(self, name) -> Topic:
        return self.topics.get(name)

    def load_topics(self, topic_list):
        topics: Mapping[str, Topic] = {}
        for topic in topic_list:
            name = topic["name"]
            destinations = topic["destinations"]
            topics[name] = Topic(name, destinations)
        providers = set(
            item for topic in topics.values() for item in topic.required_providers
        )
        self.check_providers(name, providers)
        return topics

    def parse_destination(self, destination):
        provider, *channel = destination.split(".")
        return provider, channel

    def check_providers(self, name, required_providers):
        for provider in required_providers:
            if provider == Provider.SLACK and not self.slack:
                raise ValueError(
                    f"Provider '{provider}' not configured, required by topic '{name}'"
                )
            elif provider == Provider.DISCORD and not self.discord_channel:
                raise ValueError(
                    f"Provider '{provider}' not configured, required by topic '{name}'"
                )
            elif provider == Provider.TWILIO and not self.twilio:
                raise ValueError(
                    f"Provider '{provider}' not configured, required by topic '{name}'"
                )
            elif provider == Provider.SNS and not self.sns_topic_arn:
                raise ValueError(
                    f"Provider '{provider}' not configured, required by topic '{name}'"
                )
            else:
                continue

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

    @staticmethod
    def providers_available(self) -> list:
        provider_checks = [
            (self.slack, Provider.SLACK, lambda: list(self.slack['channels'].keys())),
            (self.discord, Provider.DISCORD, lambda: list(self.discord['channels'].keys())),
            (self.twilio_from_parameter, Provider.TWILIO, lambda: {"from": list(self.twilio_from_parameter.values())[0]}),
            (self.sns_topic_arn, Provider.SNS, lambda: True)
        ]
        providers = {}
        for check, provider, cfg in provider_checks:
            if check:
                print("provider", provider, "=", cfg())
                providers[provider] = cfg()
        return providers


def auto_aws(profile_name):
    try:
        logger.debug(f"Trying aws creds, profile={profile_name}")
        boto = boto3.Session(profile_name=profile_name)
        boto.client("sts").get_caller_identity()
        logger.info("Loaded aws session")
    except boto3.exceptions.Boto3Error:
        logger.exception("No automatic boto")
        boto = None
    return boto


def manual_aws(aws):
    try:
        logger.debug("Trying conf credentials")
        key = aws.get("access_key_id")
        secret = aws.get("secret_access_key")
        region = aws.get("region")
        boto = boto3.Session(
            aws_access_key_id=key, aws_secret_access_key=secret, region_name=region
        )
        boto.client("sts").get_caller_identity()
    except boto3.exceptions.Boto3Error:
        logger.exception("No manual boto")
        boto = None
    return boto


def load_config():
    conf = _read_config()
    if not conf:
        raise FileNotFoundError("No botschaft configuration file found!")
    providers = conf.get("providers", {})
    aws = providers.get("aws", {})
    if aws:
        boto = None
        profile_name = aws.get("profile")
        boto = auto_aws(profile_name=profile_name)
        if not boto:
            boto = manual_aws(aws)
        if not boto:
            logger.exception("Unable to load AWS client")
            raise ValueError("Unable to load AWS client!")
    else:
        boto = None
    schema = BotschaftConfigSchema()
    config = schema.load(conf)
    config.boto = boto
    return config


def _read_config():
    files = [(".json", json.load), (".yaml", YAML().load), (".toml", toml.load)]
    for ext, load in files:
        fn = f"botschaft{ext}"
        try:
            with open(fn, "r") as f:
                conf = load(f)
            return conf
        except Exception as e:
            continue


_config = load_config()


def get_config():
    return _config
