# Signal Bot Framework

Python package to build your own Signal bots. To run the the bot you need to start the [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) service and link your device with it. Please refer to that project for more details.

## Classes and API

*Documentation work in progress. Feel free to open an issue for questions.*

### Example Bot

See `example` folder for a complete example on how to use the library. To run it, you need to define following env variables:
- `SIGNAL_SERVICE`: Address of the signal service without protocol, e.g. `127.0.0.1:8080`
- `PHONE_NUMBER`: Phone number of the bot, e.g. `+49123456789`
- `GROUP_ID`: Group that the bot should listen to. Currently, only groups are supported.
- `GROUP_SECRET`: Group secret / internal_id. You can get it by calling `/v1/groups/{number}/{groupid}`, see [API documentation](https://bbernhard.github.io/signal-cli-rest-api/)


### Signalbot

- `bot.listen(group_id, group_secret)`: Listen for messages in a group
- `bot.register(command)`: Register a new command
- `bot.start()`: Start the bot
- `bot.send(receiver, text, listen=False)`: Send a new message
- `bot.react(message, emoji)`: React to a message
- `bot.start_typing(receiver)`: Start typing
- `bot.stop_typing(receiver)`: Stop typing
- `bot.scheduler`: APScheduler > AsyncIOScheduler, see [here](https://apscheduler.readthedocs.io/en/3.x/modules/schedulers/asyncio.html?highlight=AsyncIOScheduler#apscheduler.schedulers.asyncio.AsyncIOScheduler)
- `bot.storage`: In-memory or Redis stroage, see `storage.py`

### Command

To implement your own commands, you need to inherent `Command` and overwrite following methods:

- `setup()`: Start any task that requires to send messages already, optional
- `describe()`: String to describe your command, optional
- `handle(context)`: Handle an incoming message. By default, any command will read any incoming message. Context can be used to easily reply (`c.send(text)`), react (`c.react(emoji)`) and to type in a group (`c.start_typing()` and `c.stop_typing()`).

## Local development and package

Increase version in `setup.cfg`, then

```
python -m build
python -m twine upload dist/*
```