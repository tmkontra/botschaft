from enum import Enum
from typing import List


class Provider(Enum):
    SLACK = "slack"
    DISCORD = "discord"
    TWILIO = "twilio"
    SNS = "sns"

    @classmethod
    def from_string(cls, provider):
        if provider == "slack":
            return Provider.SLACK
        elif provider == "discord":
            return Provider.DISCORD
        elif provider == "twilio":
            return Provider.TWILIO
        elif provider == "sns":
            return Provider.SNS
        else:
            raise ValueError(f"Invalid provider name '{provider}'")


class Destination:
    def __init__(self, provider, channel):
        self.provider = provider
        self.channel = channel


class Topic:
    def __init__(self, name, destinations):
        self.name = name
        self.destinations = self.parse_destinations(destinations)

    def params(self, message):
        for provider, channel in self.destinations.items():
            if provider == Provider.SLACK:
                params = dict(message=message, channel=channel[0])
            elif provider == Provider.DISCORD:
                params = dict(message=message, channel=channel[0])
            elif provider == Provider.TWILIO:
                params = dict(message=message, to_phone_number=channel[0])
            elif provider == Provider.SNS:
                params = dict(message=message)
            else:
                raise ValueError(f"Unsupported provider '{provider}'")
            yield provider, params

    @staticmethod
    def parse_destinations(destinations):
        dests = {}
        for dest in destinations:
            provider, *channel = dest.split(".")
            provider: Provider = Provider.from_string(provider)
            dests[provider] = channel
        return dests

    @property
    def required_providers(self) -> List[Provider]:
        return [provider for provider in self.destinations]
