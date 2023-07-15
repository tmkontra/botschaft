from typing import Optional
from fastapi import Depends, HTTPException, Header
from .config import get_config, Config


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


def message(message: Optional[str] = None, base64_message: Optional[str] = None):
    if message:
        return message
    elif base64_message:
        message = base64.b64decode(base64_message).decode("utf-8")
        return message
