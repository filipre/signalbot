from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import functools
import re
from abc import ABC, abstractmethod


from .message import Message
from .context import Context

if TYPE_CHECKING:
    from .bot import SignalBot


def regex_triggered(*by: str | re.Pattern[str]):
    def decorator_regex_triggered(func):
        @functools.wraps(func)
        async def wrapper_regex_triggered(*args, **kwargs):
            c: Context = args[1]
            text = c.message.text
            if not isinstance(text, str):
                return
            matches = [bool(re.search(pattern, text)) for pattern in by]
            if True not in matches:
                return
            return await func(*args, **kwargs)

        return wrapper_regex_triggered

    return decorator_regex_triggered


def triggered(*by: str, case_sensitive=False):
    def decorator_triggered(func):
        @functools.wraps(func)
        async def wrapper_triggered(*args, **kwargs):
            c: Context = args[1]
            text = c.message.text
            if not isinstance(text, str):
                return

            by_words = by
            if not case_sensitive:
                text = text.lower()
                by_words = [t.lower() for t in by_words]
            if text not in by_words:
                return

            return await func(*args, **kwargs)

        return wrapper_triggered

    return decorator_triggered


class Command(ABC):
    def __init__(self):
        self.bot: Optional[SignalBot] = None  # Available after calling bot.register()

    # optional
    def setup(self):
        pass

    # optional
    def describe(self) -> str:
        return None

    # overwrite
    @abstractmethod
    async def handle(self, context: Context):
        pass

    # helper method
    # deprecated: please use @triggered
    @classmethod
    def triggered(cls, message: Message, trigger_words: list[str]) -> bool:
        # Message needs to be text
        text = message.text
        if not isinstance(text, str):
            return False

        # Text must match trigger words without capitalization
        text = text.lower()
        if text in trigger_words:
            return True

        return False


class CommandError(Exception):
    pass
