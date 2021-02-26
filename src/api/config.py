from os import getenv

_env_prefix = "BOTSCHAFT__"


def get_environment_variable(name: str, required=False):
    var_name = f"{_env_prefix}__{name}"
    var = getenv(var_name)
    if required and not var:
        raise ValueError(f"Required environment variable '{var_name}' is not set!")
    else:
        return var


class Config:
    ACCESS_TOKEN = get_environment_variable("ACCESS_TOKEN")
    SLACK_API_KEY = get_environment_variable("SLACK_API_KEY")


_config = Config()


def get_config():
    return _config
