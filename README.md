# Signal Bot Framework

Python package to build your own Signal bots. To run the the bot you need to start the [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) service and link your device with it. Please refer to that project for more details. The API server must run in `json-rpc` mode.

## Getting Started

Please see https://github.com/filipre/signalbot-example for an example how to use the package and how to build a simple bot.

## Classes and API

*Documentation work in progress. Feel free to open an issue for questions.*

The package provides methods to easily listen for incoming messages and responding or reacting on them. It also provides a class to develop new commands which then can be registered within the bot.

### Signalbot

- `bot.listen(group_id, internal_id)`: Listen for messages in a group chat. `group_id` must be prefixed with `group.`
- `bot.listen(phone_number)`: Listen for messages in a user chat.
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

- `setup(self)`: Start any task that requires to send messages already, optional
- `describe(self)`: String to describe your command, optional
- `handle(self, c: Context)`: Handle an incoming message. By default, any command will read any incoming message. `Context` can be used to easily reply (`c.send(text)`), react (`c.react(emoji)`) and to type in a group (`c.start_typing()` and `c.stop_typing()`). You can use the `@triggered` decorator to listen for specific commands or you can inspect `c.message.text`.

### Unit Testing

In many cases, we can mock receiving and sending messages to speed up development time. To do so, you can use `signalbot.utils.ChatTestCase` which sets up a "skeleton" bot. Then, you can send messages using the `@chat` decorator in `signalbot.utils` like this:
```python
class PingChatTest(ChatTestCase):
    def setUp(self):
        # initialize self.singal_bot
        super().setUp()
        # all that is left to do is to register the commands that you want to test
        self.signal_bot.register(PingCommand())

    @chat("ping", "ping")
    async def test_ping(self, query, replies, reactions):
        self.assertEqual(replies.call_count, 2)
        for recipient, message in replies.results():
            self.assertEqual(recipient, ChatTestCase.group_secret)
            self.assertEqual(message, "pong")
```
In `signalbot.utils`, check out `ReceiveMessagesMock`, `SendMessagesMock` and `ReactMessageMock` to learn more about their API.

## Troubleshooting

- Check that you linked your account successfully
- Is the API server running in `json-rpc` mode?
- Can you receive messages using `wscat` (websockets) and send messages using `curl` (http)?
- Do you see incoming messages in the API logs?
- Do you see the "raw" messages in the bot's logs?
- Do you see "consumers" picking up jobs and handling incoming messages?
- Do you see the response in the bot's logs?

## Local development and package

*Section work in progress. Feel free to open an issue for questions.*

```
poetry install
poetry run pre-commit install
```

## Other Projects

There are a few other related projects similar to this one. You may want to check them out and see if it fits your needs.

|Project|Description|Language|Status|
|-------|-----------|--------|------|
|https://github.com/signalapp/libsignal-service-java|Signal Library|Java|Last change 12 Nov 2019|
|https://github.com/AsamK/signal-cli|A CLI and D-Bus interface for Signal|Java|active, build on top of https://github.com/signalapp/libsignal-service-java|
|https://github.com/bbernhard/signal-cli-rest-api|REST API Wrapper for Signal CLI|Go|active, build on top of https://github.com/AsamK/signal-cli|
|https://github.com/aaronetz/signal-bot|Bot Framework|Java|Last change 18 Feb 2021|
|https://github.com/signal-bot/signal-bot|Bot Framework|Python|Last change 6 Jul 2018|
