# Signal Bot Framework

Python package to build your own Signal bots. To run the the bot you need to start the [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) service and link your device with it. Please refer to that project for more details. The API server must run in `json-rpc` mode.

## Getting Started

Below you can find a minimal example on how to use the package.
Save it as `bot.py`.
There is also a bigger example in the `example` folder.

```python
import os
from signalbot import SignalBot, Command, Context
from commands import PingCommand


class PingCommand(Command):
    async def handle(self, c: Context):
        if c.message.text == "Ping":
            await c.send("Pong")


if __name__ == "__main__":
    bot = SignalBot({
        "signal_service": os.environ["SIGNAL_SERVICE"],
        "phone_number": os.environ["PHONE_NUMBER"]
    })
    bot.register(PingCommand()) # all contacts and groups
    bot.start()
```

Please check out https://github.com/bbernhard/signal-cli-rest-api#getting-started to learn about [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) and [signal-cli](https://github.com/AsamK/signal-cli). A good first step is to make the example above work.

1. Run signal-cli-rest-api in `normal` mode first.
```bash
docker run -p 8080:8080 \
    -v $(pwd)/signal-cli-config:/home/.local/share/signal-cli \
    -e 'MODE=normal' bbernhard/signal-cli-rest-api:latest
```

2. Open http://127.0.0.1:8080/v1/qrcodelink?device_name=local to link your account with the signal-cli-rest-api server

3. In your Signal app, open settings and scan the QR code. The server can now receive and send messages. The access key will be stored in `$(PWD)/signal-cli-config`.

4. Restart the server in `json-rpc` mode.
```bash
docker run -p 8080:8080 \
    -v $(pwd)/signal-cli-config:/home/.local/share/signal-cli \
    -e 'MODE=json-rpc' bbernhard/signal-cli-rest-api:latest
```

5. The logs should show something like this. You can also confirm that the server is running in the correct mode by visiting http://127.0.0.1:8080/v1/about.
```
...
time="2022-03-07T13:02:22Z" level=info msg="Found number +491234567890 and added it to jsonrpc2.yml"
...
time="2022-03-07T13:02:24Z" level=info msg="Started Signal Messenger REST API"
```

6. Install `signalbot` and start your python script. You need to pass following environment variables to make the example run:
- `SIGNAL_SERVICE`: Address of the signal service without protocol, e.g. `127.0.0.1:8080`
- `PHONE_NUMBER`: Phone number of the bot, e.g. `+49123456789`

```bash
export SIGNAL_SERVICE="127.0.0.1"
export PHONE_NUMBER="+49123456789"
pip install signalbot
python bot.py
```

7. The logs should indicate that one "producer" and three "consumers" have started. The producer checks for new messages sent to the linked account using a web socket connection. It creates a task for every registered command and the consumers work off the tasks. In case you are working with many blocking function calls, you may need to adjust the number of consumers such that the bot stays reactive.
```
INFO:root:[Bot] Producer #1 started
INFO:root:[Bot] Consumer #1 started
INFO:root:[Bot] Consumer #2 started
INFO:root:[Bot] Consumer #3 started
```

8. Send the message `Ping` (case sensitive) to the number that the bot is listening to. The bot (i.e. the linked account) should respond with a `Pong`. Confirm that the bot received a raw message, that the consumer worked on the message and that a new message has been sent.
```
INFO:root:[Raw Message] {"envelope":{"source":"+49123456789","sourceNumber":"+49123456789","sourceUuid":"fghjkl-asdf-asdf-asdf-dfghjkl","sourceName":"René","sourceDevice":3,"timestamp":1646000000000,"syncMessage":{"sentMessage":{"destination":null,"destinationNumber":null,"destinationUuid":null,"timestamp":1646000000000,"message":"Pong","expiresInSeconds":0,"viewOnce":false,"groupInfo":{"groupId":"asdasdfweasdfsdfcvbnmfghjkl=","type":"DELIVER"}}}},"account":"+49123456789","subscription":0}
INFO:root:[Bot] Consumer #2 got new job in 0.00046 seconds
INFO:root:[Bot] Consumer #2 got new job in 0.00079 seconds
INFO:root:[Bot] Consumer #2 got new job in 0.00093 seconds
INFO:root:[Bot] Consumer #2 got new job in 0.00106 seconds
INFO:root:[Bot] New message 1646000000000 sent:
Pong
```

## Classes and API

*Documentation work in progress. Feel free to open an issue for questions.*

The package provides methods to easily listen for incoming messages and responding or reacting on them. It also provides a class to develop new commands which then can be registered within the bot.

### Signalbot

- `bot.register(command, contacts=True, groups=True)`: Register a new command, listen in all contacts and groups, same as `bot.register(command)`
- `bot.register(command, contacts=False, groups=["Hello World"])`: Only listen in the "Hello World" group
- `bot.register(command, contacts=["+49123456789"], groups=False)`: Only respond to one contact
- `bot.start()`: Start the bot
- `bot.send(receiver, text)`: Send a new message
- `bot.react(message, emoji)`: React to a message
- `bot.start_typing(receiver)`: Start typing
- `bot.stop_typing(receiver)`: Stop typing
- `bot.scheduler`: APScheduler > AsyncIOScheduler, see [here](https://apscheduler.readthedocs.io/en/3.x/modules/schedulers/asyncio.html?highlight=AsyncIOScheduler#apscheduler.schedulers.asyncio.AsyncIOScheduler)

### Persistent storage

By default the `bot.storage` is in-memory.
Any changes are lost when the bot is stopped or reseted.
For persistent storage to disk, check the SQLite or Redis storage in `storage.py`.

### Command

To implement your own commands, you need to inherent `Command` and overwrite following methods:

- `setup(self)`: Start any task that requires to send messages already, optional
- `describe(self)`: String to describe your command, optional
- `handle(self, c: Context)`: Handle an incoming message. By default, any command will read any incoming message. `Context` can be used to easily send (`c.send(text)`), reply (`c.reply(text)`), react (`c.react(emoji)`) and to type in a group (`c.start_typing()` and `c.stop_typing()`). You can use the `@triggered` decorator to listen for specific commands, the `@regex_triggered` decorator to listen for regular expressions, or you can inspect `c.message.text`.

### Unit Testing

*Note: deprecated, I want to switch to pytest eventually*

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

```bash
poetry install
poetry run pre-commit install
```

## Other Projects

There are a few other related projects similar to this one. You may want to check them out and see if it fits your needs.

|Project|Description|Language|
|-------|-----------|--------|
|https://github.com/lwesterhof/semaphore|Bot Framework|Python|
|https://git.sr.ht/~nicoco/aiosignald|signald Library / Bot Framework|Python|
|https://gitlab.com/stavros/pysignald/|signald Library / Bot Framework|Python|
|https://gitlab.com/signald/signald-go|signald Library|Go|
|https://github.com/signal-bot/signal-bot|Bot Framework using Signal CLI|Python|
|https://github.com/bbernhard/signal-cli-rest-api|REST API Wrapper for Signal CLI|Go|
|https://github.com/bbernhard/pysignalclirestapi|Python Wrapper for REST API|Python|
|https://github.com/AsamK/signal-cli|A CLI and D-Bus interface for Signal|Java|
|https://github.com/signalapp/libsignal-service-java|Signal Library|Java|
|https://github.com/aaronetz/signal-bot|Bot Framework|Java|
