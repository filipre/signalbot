from .message import Message
from .context import Context


class Command:
    # optional
    def setup(self):
        pass

    # optional
    def describe(self) -> str:
        return None

    # overwrite
    async def handle(self, context: Context):
        raise NotImplementedError

    # helper method
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
