# ![logo](docs/logo.png)

Pronounced ["boat-shahft"](https://forvo.com/word/botschaft/)

# What is botschaft?

Botschaft is unified messaging & notifications appliance. Want to text yourself when a long-running task completes, but don't want to remember your account id or store credentials on your job server? Or maybe you want to send a slack message, a discord message, and an SNS message, all at once? Define a botschaft topic and hit it whenever you want.

It's as easy as `curl http://my.botschaft.server/slack?channel=general&message=Hello!`

# No, _what is 'botschaft'_?

> `Botschaft`, German, noun, feminine (genitive Botschaft, plural Botschaften)

Botschaft is "message" in German. The "bot" prefix seemed appropriate for what is essentially a notification bot.

# Features

- Dead simple HTTP API
- Declarative configuration
- "Topics", flexible, customizable groups of destinations

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

See the example configuration files [here](/example).


# Running Botschaft

To start a botschaft instance, define your config file and start the container like so:

> docker run -v /path/to/my/botschaft.toml:/botschaft.toml -p8000:8000 -it ttymck/botschaft:latest

Or use docker-compose, like the [example here](/example/docker-compose.yaml)

# Web API Reference

A running botschaft instance provides OpenAPI docs at `${botschaft-uri}/docs`

## Message

Every route takes a `message`, which can be given by the `message` or `message_base64` parameter (if both are set, `message` is used). `message_base64` will first be base64 decoded before being sent.

## Provider parameters

Each provider may take further parameters, generally to indicate the specific destination channel (Slack channel, SMS phone number, etc). These may correspond to the provider configuration

- Slack: `channel`
- Discord: `channel`
- Twilio: `to`
- Sns: `null`


