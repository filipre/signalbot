from .message import Message


class Command:
    def __init__(self):
        self.bot = None

    # optional
    def init(self):
        """init method to define or perform tasks before listening for messages
        you can access self.bot to access the scheduler or to send messages already"""
        pass

    # optional
    def description(self) -> str:
        """short description of the command"""
        return None

    # overwrite
    async def handle(self, message: Message):
        """handle method to react on messages, see commands folder for examples"""
        raise NotImplementedError

    # helper method
    @classmethod
    def triggered(cls, message: Message, trigger_words: list[str]) -> bool:
        """helper method to check whether we have to act or not"""
        
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
