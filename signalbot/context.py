# from .bot import Signalbot # TODO: figure out how to enable this for typing
from .message import Message


class Context:
    def __init__(self, bot, message: Message):
        self.bot = bot
        self.message = message

    async def send(
        self,
        text: str,
        base64_attachments: list = None,
        mentions: list = None,
        text_mode: str = None,
    ):
        return await self.bot.send(
            self.message.recipient(),
            text,
            base64_attachments=base64_attachments,
            mentions=mentions,
            text_mode=text_mode,
        )

    async def reply(
        self,
        text: str,
        base64_attachments: list = None,
        mentions: list = None,
        text_mode: str = None,
    ):
        return await self.bot.send(
            self.message.recipient(),
            text,
            base64_attachments=base64_attachments,
            quote_author=self.message.source,
            quote_mentions=self.message.mentions,
            quote_message=self.message.text,
            quote_timestamp=self.message.timestamp,
            mentions=mentions,
            text_mode=text_mode,
        )

    async def react(self, emoji: str):
        await self.bot.react(self.message, emoji)

    async def start_typing(self):
        await self.bot.start_typing(self.message.recipient())

    async def stop_typing(self):
        await self.bot.stop_typing(self.message.recipient())
