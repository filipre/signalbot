# Signal Bot Framework

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/signalbot?period=monthly&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=BRIGHTGREEN&left_text=Monthly+downloads)](https://pepy.tech/projects/signalbot)
[![image](https://img.shields.io/pypi/v/signalbot.svg)](https://pypi.python.org/pypi/signalbot)
[![image](https://img.shields.io/pypi/l/signalbot.svg)](https://pypi.python.org/pypi/signalbot)
[![CI](https://github.com/signalbot-org/signalbot/actions/workflows/ci.yaml/badge.svg)](https://github.com/signalbot-org/signalbot/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/signalbot-org/signalbot/graph/badge.svg?token=N3ZA5MTU2P)](https://codecov.io/gh/signalbot-org/signalbot)

Python package to build your own Signal bots.

## Installation

See the [getting started](https://signalbot-org.github.io/signalbot/getting_started) section in the documentation.

## Minimal bot

This is what a minimal bot using signalbot looks like:

```python
import os
import logging
from signalbot import SignalBot, Config, Command, Context, triggered, enable_console_logging


class PingCommand(Command):
    @triggered("Ping")
    async def handle(self, c: Context) -> None:
        await c.send("Pong")


if __name__ == "__main__":
    enable_console_logging(logging.INFO)

    bot = SignalBot(
        Config(
            signal_service=os.environ["SIGNAL_SERVICE"],
            phone_number=os.environ["PHONE_NUMBER"],
        )
    )
    bot.register(PingCommand()) # Run the command for all contacts and groups
    bot.start()
```

## Help

See the [documentation](https://signalbot-org.github.io/signalbot/) for more details.

## Other Projects

There are a few other projects similar to this one. You may want to check them out and see if they fit your needs.

|Project|Description|Language|Maintained|
|-------|:---------:|:------:|:------:|
|https://github.com/AsamK/signal-cli|A CLI and D-Bus interface for Signal|Java|✅|
|https://github.com/bbernhard/pysignalclirestapi|Python Wrapper for REST API|Python|✅|
|https://github.com/bbernhard/signal-cli-rest-api|REST API Wrapper for Signal CLI|Go|✅|
|https://github.com/signal-bot/signal-bot|Bot Framework using Signal CLI|Python|❌|
|https://github.com/signalapp/libsignal-service-java|Signal Library|Java|❌|
|https://github.com/aaronetz/signal-bot|Bot Framework|Java|❌|
|https://gitlab.com/signald/signald|A socket interface for Signal|Java|❌|
|https://codeberg.org/lazlo/semaphore|signald Library / Bot Framework|Python|❌|
|https://git.sr.ht/~nicoco/aiosignald|signald Library / Bot Framework|Python|❌|
|https://gitlab.com/stavros/pysignald|signald Library / Bot Framework|Python|❌|
|https://gitlab.com/signald/signald-go|signald Library|Go|❌|
