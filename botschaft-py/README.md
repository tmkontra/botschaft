# botschaft-py

:warning: This is the deprecated legacy implementation of Botschaft.

# Configuration

Botschaft currently supports the following notification "providers":

- Slack
- Discord
- Twilio
- SNS

All providers are supported out of the box, and are enabled by specifying the corresponding section and parameters in the botschaft config file (see next section)

Topics are custom groups of provider destinations for a single message, for instance: Slack #alerts + Discord #general.

Botschaft optionally supports bearer token authentication, configured by setting the `BOTSCHAFT__ACCESS_TOKEN` environment variable. **When that variable is not set, the API is unauthenticated**.

## Botschaft Config File

The botschaft config file can be defined as `json`, `yaml` or `toml`. Any combination of providers can be defined.

Botschaft will try its best to verify a valid configuration at start-up. If a topic requires a specific provider, it will make sure that provider section is specified in the config.

When any AWS providers are configured (currently only SNS), botschaft will load the AWS credentials and test the connection to AWS at startup (using [sts.get_caller_identity](https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html)).

Botschaft will first try loading the AWS credentials and profile via boto3 (environment, shared config file, aws cli configuration, etc.), but will fall back to optional Access Key and Secret Key values in the botschaft config file.

See the example configuration files [here](./example).


# Running Botschaft

To start a botschaft instance, define your config file and start the container like so:

> docker run -v /path/to/my/botschaft.toml:/botschaft.toml -p8000:8000 -it ttymck/botschaft:latest

Or use docker-compose, like the [example here](./example/docker-compose.yaml)

# Web API Reference

A running botschaft instance provides OpenAPI docs at `${botschaft-uri}/docs`

You can view a copy of the OpenAPI docs here: [openapi.json](./example/openapi.json)

## Routes

Every provider exposes a `GET` and a `POST` route, accepting the `message` and any other provider-specific parameters (see below) as either query parameters or a json body, respectively. The behavior of the `GET` and `POST` are identical, you are free to use either one based on personal perference (or, if your messages are too long for URLs, the `POST` will accomodate them).

## Message

Every route takes a `message`, which can be given by the `message` or `message_base64` parameter (if both are set, `message` is used). `message_base64` will first be base64 decoded before being sent.

## Provider parameters

Each provider may take further parameters, generally to indicate the specific destination channel (Slack channel, SMS phone number, etc). These may correspond to the provider configuration

- Slack: `channel`
- Discord: `channel`
- Twilio: `to`
- Sns: `null`
