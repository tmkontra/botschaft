# ![logo](docs/logo.png)

Pronounced ["boat-shahft"](https://forvo.com/word/botschaft/)

> :warning: The original Python implementation is deprecated, and has been moved to `botschaft-py`.
>
> :construction: Development on Botschaft will continue with `botschaft_otp`, implemented in Elixir. This document refers only to botschaft_otp.

# What is Botschaft?

Botschaft is unified messaging & notifications appliance. Use Botschaft to send messages via Slack, Discord, and Telegram. Group multiple destinations into "Topics" and send messages to multiple destinations with a single request.

It's as easy as `curl http://my.botschaft.server/slack?channel=general&message=Hello!`

# No, _what is 'botschaft'_?

> `Botschaft`, German, noun, feminine (genitive Botschaft, plural Botschaften)

Botschaft is "message" in German. The "bot" prefix seemed appropriate for what is essentially a notification bot.

# Why use Botschaft?

- Many teams start out using one messaging provider and later switch to another. Maybe you use Slack today, but next year your team might move to Discord. Avoid the headache of re-implementing outgoing messages by targeting Botschaft instead. This way, you can change the declarative Botschaft configuration instead of changing your app source code.
- If you have multiple application deployments and want to avoid proliferating Slack or Discord credentials and secrets. Centralize the messaging API credentials in Botschaft, and route your messages through it.
- If you want to give non-programmers control over multiple messaging channels and the formatting of the messages. Botschaft supports messages templates. Change your messages without re-deploying your application (and without restarting Botschaft!)

# Features

- Dead simple HTTP API
- Declarative configuration
- "Topics", flexible, customizable groups of destinations
- Configuration reloading - no restart required
