from __future__ import annotations

import functools
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from signalbot.context import Context  # noqa: TC001

if TYPE_CHECKING:
    from signalbot.bot import SignalBot


def regex_triggered(*by: str | re.Pattern[str]):  # noqa: ANN201
    def decorator_regex_triggered(func):  # noqa: ANN001, ANN202
        @functools.wraps(func)
        async def wrapper_regex_triggered(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            c: Context = args[1]
            text = c.message.text
            if not isinstance(text, str):
                return None
            matches = [bool(re.search(pattern, text)) for pattern in by]
            if True not in matches:
                return None
            return await func(*args, **kwargs)

        return wrapper_regex_triggered

    return decorator_regex_triggered


def triggered(*by: str, case_sensitive=False):  # noqa: ANN001, ANN201
    def decorator_triggered(func):  # noqa: ANN001, ANN202
        @functools.wraps(func)
        async def wrapper_triggered(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            c: Context = args[1]
            text = c.message.text
            if not isinstance(text, str):
                return None

            by_words = by
            if not case_sensitive:
                text = text.lower()
                by_words = [t.lower() for t in by_words]
            if text not in by_words:
                return None

            return await func(*args, **kwargs)

        return wrapper_triggered

    return decorator_triggered


class Command(ABC):
    def __init__(self):  # noqa: ANN204
        self.bot: SignalBot | None = None  # Available after calling bot.register()

    # optional
    def setup(self) -> None:  # noqa: B027
        pass

    # optional
    def describe(self) -> str | None:
        return None

    # overwrite
    @abstractmethod
    async def handle(self, context: Context) -> None:
        pass


class CommandError(Exception):
    pass
