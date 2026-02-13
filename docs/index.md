# Signalbot

Python package to build your own Signal bots.

The package provides methods to easily listen for incoming messages and responding or reacting on them.
It also provides a class to develop new commands which then can be registered within the bot.

Here is minimal example of what that looks like:
```python
--8<-- "example/simple_bot.py"
```

To set it up follow the steps in the [getting started page](getting_started.md).

### Common methods

The bot can do a lot more, here is a quick overview of the most common methods:

- `bot.register(command, contacts=True, groups=True)`: Register a new command, listen in all contacts and groups, same as `bot.register(command)`
- `bot.register(command, contacts=False, groups=["Hello World"])`: Only listen in the "Hello World" group
- `bot.register(command, contacts=["+49123456789"], groups=False)`: Only respond to one contact
- `bot.start()`: Start the bot
- `bot.send(receiver, text)`: Send a new message
- `bot.react(message, emoji)`: React to a message
- `bot.start_typing(receiver)`: Start typing
- `bot.stop_typing(receiver)`: Stop typing
- `bot.send(receiver, text, edit_timestamp=timestamp)`: Edit a previously sent message
- `bot.remote_delete(receiver, timestamp)`: Delete a previously sent message
- `bot.receipt(message, receipt_type)`: Mark a message as read
- `bot.update_group(group_id, avatar, description, expiration, name)`: Change group settings
- `bot.delete_attachment(attachment_filename)`: Delete the local copy of an attachment
- `bot.scheduler`: APScheduler > AsyncIOScheduler, see [here](https://apscheduler.readthedocs.io/en/3.x/modules/schedulers/asyncio.html?highlight=AsyncIOScheduler#apscheduler.schedulers.asyncio.AsyncIOScheduler)
