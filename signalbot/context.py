from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Any
from copy import deepcopy

from .message import Message

if TYPE_CHECKING:
    from .bot import SignalBot


class Context:
    def __init__(self, bot: SignalBot, message: Message):
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
        mentions: (
            list[dict[str, Any]] | None
        ) = None,  # [{ "author": "uuid" , "start": 0, "length": 1 }]
        text_mode: str = None,
    ):
        send_mentions = self._convert_receive_mentions_into_send_mentions(
            self.message.mentions
        )
        return await self.bot.send(
            self.message.recipient(),
            text,
            base64_attachments=base64_attachments,
            quote_author=self.message.source,
            quote_mentions=send_mentions,
            quote_message=self.message.text,
            quote_timestamp=self.message.timestamp,
            mentions=mentions,
            text_mode=text_mode,
        )

    async def react(self, emoji: str):
        await self.bot.react(self.message, emoji)

    async def receipt(self, receipt_type: Literal["read", "viewed"]):
        await self.bot.receipt(self.message, receipt_type)

    async def start_typing(self):
        await self.bot.start_typing(self.message.recipient())

    async def stop_typing(self):
        await self.bot.stop_typing(self.message.recipient())

    def _convert_receive_mentions_into_send_mentions(
        self, mentions: list[dict[str, Any]] | None = None
    ):
        if mentions is None:
            return None

        send_mentions = deepcopy(mentions)
        for mention in send_mentions:
            if "author" not in mention:
                mention["author"] = mention["uuid"]
        return send_mentions
