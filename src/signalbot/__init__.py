import importlib.metadata

from signalbot.api import (
    ConnectionMode,
    ReceiveMessagesError,
    SendMessageError,
    SignalAPI,
)
from signalbot.bot import (
    LOGGER_NAME,
    MIN_SIGNAL_CLI_REST_API_VERSION,
    SignalBot,
    enable_console_logging,
)
from signalbot.bot_config import Config, InMemoryConfig, RedisConfig, SQLiteConfig
from signalbot.command import (
    Command,
    CommandError,
    reaction_triggered,
    regex_triggered,
    triggered,
)
from signalbot.context import Context
from signalbot.link_previews import LinkPreview
from signalbot.message import Message, MessageType, Quote, UnknownMessageFormatError
from signalbot.reaction import Reaction

__all__ = [
    "LOGGER_NAME",
    "MIN_SIGNAL_CLI_REST_API_VERSION",
    "Command",
    "CommandError",
    "Config",
    "ConnectionMode",
    "Context",
    "InMemoryConfig",
    "LinkPreview",
    "Message",
    "MessageType",
    "Quote",
    "Reaction",
    "ReceiveMessagesError",
    "RedisConfig",
    "SQLiteConfig",
    "SendMessageError",
    "SignalAPI",
    "SignalBot",
    "UnknownMessageFormatError",
    "enable_console_logging",
    "reaction_triggered",
    "regex_triggered",
    "triggered",
]

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
