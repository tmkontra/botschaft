# ![logo](docs/logo.png)

Pronounced ["boat-shahft"](https://forvo.com/word/botschaft/)

> :warning: The original Python implementation is deprecated, and has been moved to `botschaft-py`.
>
> :construction: Development on Botschaft will continue with `botschaft_otp`, implemented in Elixir.

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
