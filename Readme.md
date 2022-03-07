# Signal Bot Framework

Python package to build your own Signal bots. To run the the bot you need to start the [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) service and link your device with it. Please refer to that project for more details. The bot must run in `json-rpc` mode.

## Getting Started

*Also see https://github.com/bbernhard/signal-cli-rest-api#getting-started*

1. Go into the `example` folder and run [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) in `normal` mode first.
```bash
docker run -p 8080:8080 \
    -v $(PWD)/signal-cli-config:/home/.local/share/signal-cli \
    -e 'MODE=normal' bbernhard/signal-cli-rest-api:0.57
```

2. Open http://127.0.0.1:8080/v1/qrcodelink?device_name=local to link your account with the signal-cli-rest-api server

3. In your Signal app, open settings and scan the QR code. The server can now receive and send messages. The access key is stored in `$(PWD)/signal-cli-config`.

4. Stop the server and restart it in `json-rpc` mode. 
```bash
docker run -p 8080:8080 \
    -v $(PWD)/signal-cli-config:/home/.local/share/signal-cli \
    -e 'MODE=json-rpc' bbernhard/signal-cli-rest-api:0.57
```

5. In the logs, you should see something like
```
...
time="2022-03-07T13:02:22Z" level=info msg="Found number +491234567890 and added it to jsonrpc2.yml"
...
time="2022-03-07T13:02:24Z" level=info msg="Started Signal Messenger REST API"
```

6. You can confirm that the server is running in the correct mode by visiting http://127.0.0.1:8080/v1/about
```json
{"versions":["v1","v2"],"build":2,"mode":"json-rpc","version":"0.57"}
```

7. Install `signalbot` and start `bot.py`. You need to pass following environment variables to make the example run:
- `SIGNAL_SERVICE`: Address of the signal service without protocol, e.g. `127.0.0.1:8080`
- `PHONE_NUMBER`: Phone number of the bot, e.g. `+49123456789`
- `GROUP_ID`: Group that the bot should listen to. Currently, only groups are supported.
- `GROUP_SECRET`: Group secret / internal_id. You can get it by calling `http://127.0.0.1:8080/v1/groups/{number}/{groupid}`, see [API documentation](https://bbernhard.github.io/signal-cli-rest-api/)

```bash
pip install signalbot
SIGNAL_SERVICE=... PHONE_NUMBER=... GROUP_ID=... GROUP_SECRET=... python bot.py
```

8. The logs should indicate that one "producer" and three "consumers" started. The producer checks for new messages sent to the linked account using a web socket connection. It creates a task for every registered command and the consumers work off the tasks.
```
INFO:root:[Bot] Producer #1 started
INFO:root:[Bot] Consumer #1 started
INFO:root:[Bot] Consumer #2 started
INFO:root:[Bot] Consumer #3 started
```

9. Send the message `ping` (case sensitive) to the group that the bot is listening to. The bot (i.e. you) should respond with a `pong`. You should see that the bot received a raw message, that the consumer worked on the message and that a new message has been sent.
```
INFO:root:[Raw Message] {"envelope":{"source":"+49123456789","sourceNumber":"+49123456789","sourceUuid":"fghjkl-asdf-asdf-asdf-dfghjkl","sourceName":"René","sourceDevice":3,"timestamp":1646000000000,"syncMessage":{"sentMessage":{"destination":null,"destinationNumber":null,"destinationUuid":null,"timestamp":1646000000000,"message":"pong","expiresInSeconds":0,"viewOnce":false,"groupInfo":{"groupId":"asdasdfweasdfsdfcvbnmfghjkl=","type":"DELIVER"}}}},"account":"+49123456789","subscription":0}
INFO:root:[Bot] Consumer #2 got new job in 0.00046 seconds
INFO:root:[Bot] Consumer #2 got new job in 0.00079 seconds
INFO:root:[Bot] Consumer #2 got new job in 0.00093 seconds
INFO:root:[Bot] Consumer #2 got new job in 0.00106 seconds
INFO:root:[Bot] New message 1646000000000 sent:
pong
```

## Classes and API

*Documentation work in progress. Feel free to open an issue for questions.*

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