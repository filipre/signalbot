Install it with
```bash
pip install signalbot
```

Below you can find a minimal example on how to use the package.
Save it as `bot.py`.
There is also a bigger example in the [examples section](examples/api_overview.md).

```python
--8<-- "examples/simple_bot.py"
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
export SIGNAL_SERVICE="127.0.0.1:8080"
export PHONE_NUMBER="+49123456789"
pip install signalbot
python bot.py
```

By default, `SignalBot` starts with `HTTPS/WSS` and can fallback to `HTTP/WS` if needed.
Set `connection_mode` in the config to control behavior:
- `ConnectionMode.HTTPS_ONLY`: only `HTTPS/WSS`
- `ConnectionMode.HTTP_ONLY`: only `HTTP/WS`
- `ConnectionMode.AUTO`: start with `HTTPS/WSS`, fallback to `HTTP/WS` (default)

7. The logs should indicate that one "producer" and three "consumers" have started. The producer checks for new messages sent to the linked account using a web socket connection. It creates a task for every registered command and the consumers work off the tasks. In case you are working with many blocking function calls, you may need to adjust the number of consumers such that the bot stays reactive.
```
<date> signalbot [WARNING] - __init__ - [Bot] Could not initialize Redis and no SQLite DB name was given. In-memory storage will be used. Restarting will delete the storage! Add storage: {'type': 'in-memory'} to the config to silence this error.
<date> signalbot [INFO] - _detect_groups - [Bot] 3 groups detected
<date> signalbot [INFO] - _produce - [Bot] Producer #1 started
<date> signalbot [INFO] - _consume - [Bot] Consumer #1 started
<date> signalbot [INFO] - _consume - [Bot] Consumer #2 started
<date> signalbot [INFO] - _consume - [Bot] Consumer #3 started
```

8. Send the message `Ping` (case sensitive) to the number that the bot is listening to. The bot (i.e. the linked account) should respond with a `Pong`. Confirm that the bot received a raw message, that the consumer worked on the message and that a new message has been sent.
```
<date> signalbot [INFO] - _produce - [Raw Message] {"envelope": <raw message dictionary>}
<date> signalbot [INFO] - _consume_new_item - [Bot] Consumer #2 got new job in 0.00046 seconds
<date> signalbot [INFO] - _produce - [Raw Message] {"envelope": <raw message dictionary>}
<date> signalbot [INFO] - send - [Bot] New message 1760797696983 sent:
Pong
```
