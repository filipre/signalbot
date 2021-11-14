# Signal Bot Framework

Python package to build your own Signal bots. To run the the bot you need to start the [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) service and link your device with it.

## Todos

- Examples on how to use the package
- Documentation
- Github actions to build on release

## Classes and API

### Signalbot

```python
bot = Signalbot({
    "signal_service": "127.0.0.1:8080"
    "phone_number": "+49123456789"
    "storage": {
        "redis_host": "redis"
        "redis_port": 6379
    }
})
```

- `bot.listen(group_id, group_secret)`: Listen for messages in a group
- `bot.register(command)`: Register a new command
- `bot.start()`: Start the bot
- `bot.send(receiver, text)`: Send a new message
- `bot.react(message, emoji)`: React to a message
- `bot.start_typing(receiver)`: Start typing
- `bot.stop_typing(receiver)`: Stop typing
- `bot.scheduler`: APScheduler > AsyncIOScheduler, see [here](https://apscheduler.readthedocs.io/en/3.x/modules/schedulers/asyncio.html?highlight=AsyncIOScheduler#apscheduler.schedulers.asyncio.AsyncIOScheduler)
- `bot.storage`: In-memory or Redis stroage, see `storage.py`

### Command

- `cmd.setup()`: Start any task that requires to send messages already, optional
- `cmd.describe()`: String to describe your command, optional
- `cmd.handle(context)`: Handle an incoming message. By default, any command will read any incoming message. Context can be used to easily reply (`c.send(text)`), react (`c.react(emoji)`) and to type in a group (`c.start_typing()` and `c.stop_typing()`).