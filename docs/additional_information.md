## Logging

The logger name for the library is `"signalbot"`.
It does not have any handlers attached, for convenience the `enable_console_logging(level)` function is provided.

## Persistent storage

By default the `bot.storage` is in-memory.
Any changes are lost when the bot is stopped or reseted.
For persistent storage to disk, check the SQLite or Redis storage in `storage.py`.

## Real world bot examples

There are many real world examples of bot implementations using this library.
Check the whole list at https://github.com/signalbot-org/signalbot/network/dependents
