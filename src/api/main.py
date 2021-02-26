from typing import Optional

from fastapi import FastAPI, Header, Depends
from fastapi.exceptions import HTTPException

from .config import get_config, Config
from .slack import slack_message, SlackMessage


def authorize(
    config: Config = Depends(get_config), authorization: Optional[str] = Header(None)
):
    if config.ACCESS_TOKEN and authorization:
        try:
            if authorization.split(" ")[1] == config.ACCESS_TOKEN:
                return True
            else:
                raise HTTPException(status_code=401)
        except IndexError:
            raise HTTPException(status_code=401)
    elif config.ACCESS_TOKEN:
        raise HTTPException(status_code=401)
    else:
        return True


api = FastAPI(
    dependencies=[
        Depends(authorize),
    ]
)


@api.get("/slack")
def index(message: SlackMessage = Depends(slack_message)):
    message.send()
    return f"Sent '{message.message}' to #{message.channel}"
