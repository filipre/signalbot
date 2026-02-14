from __future__ import annotations

import functools
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")

if TYPE_CHECKING:
    from signalbot.bot import SignalBot
    from signalbot.context import Context


def regex_triggered(
    *by: str | re.Pattern[str],
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to trigger a command if the message text matches any of the provided
    regex patterns.

    Args:
        *by: A variable number of strings or compiled regex patterns to match the
        message text against.
    """

    def decorator_regex_triggered(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper_regex_triggered(
            *args: P.args, **kwargs: P.kwargs
        ) -> T | None:
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


def triggered(
    *by: str, case_sensitive: bool = False
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to trigger a command if the message text matches any of the provided
    strings.

    Args:
        *by: A variable number of strings to match the message text against.
        case_sensitive: Whether the matching should be case sensitive.
    """

    def decorator_triggered(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper_triggered(*args: P.args, **kwargs: P.kwargs) -> T | None:
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
    """Abstract base class for commands.

    To create a command, subclass this class and implement the `handle` method.
    Then, register the command with the bot using `bot.register(CommandSubclass)`.
    """

    def __init__(self) -> None:
        # The bot attribute is assigned after calling bot.register(Command())
        self.bot: SignalBot | None = None

    def setup(self) -> None:
        """Optional setup method that can be overridden by subclasses.
        This method is called after the command is registered with the bot but
        before any data is retrieved, so it cannot access the group ids.
        """
        return

    @abstractmethod
    async def handle(self, context: Context) -> None:
        """Abstract method to handle a command.
        This method must be implemented by subclasses to define the behavior of the
            command.
        Args:
            context: Chat context containing the received message and other information.
        """


class CommandError(Exception):
    pass
