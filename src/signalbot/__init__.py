import importlib.metadata

from signalbot.api import ReceiveMessagesError, SendMessageError, SignalAPI
from signalbot.bot import SignalBot, enable_console_logging
from signalbot.command import Command, CommandError, regex_triggered, triggered
from signalbot.context import Context
from signalbot.link_previews import LinkPreview
from signalbot.message import Message, MessageType, Quote, UnknownMessageFormatError

__all__ = [
    "Command",
    "CommandError",
    "Context",
    "LinkPreview",
    "Message",
    "MessageType",
    "Quote",
    "ReceiveMessagesError",
    "SendMessageError",
    "SignalAPI",
    "SignalBot",
    "UnknownMessageFormatError",
    "enable_console_logging",
    "regex_triggered",
    "triggered",
]

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
