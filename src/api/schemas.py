from typing import Optional, List, Mapping
from pydantic import BaseModel

from api import config
from api.model import Provider

class Config(BaseModel):
    providers: Mapping
    topics: List

def config_to_response(config: config.Config):
    p = config.provider_info
    return Config(providers=config.provider_info, topics=list(config.topics.keys()))