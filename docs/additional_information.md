## Logging

The logger name for the library is `"signalbot"`.
It does not have any handlers attached, for convenience the `enable_console_logging(level)` function is provided.

## Persistent storage

By default the `bot.storage` is in-memory.
Any changes are lost when the bot is stopped or reseted.
For persistent storage to disk, check the SQLite or Redis storage in `storage.py`.
