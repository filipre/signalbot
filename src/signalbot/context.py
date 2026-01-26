from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from signalbot.bot import SignalBot
    from signalbot.link_previews import LinkPreview
    from signalbot.message import Message


class Context:
    def __init__(self, bot: SignalBot, message: Message) -> None:
        self.bot = bot
        self.message = message

    async def send(  # noqa: PLR0913
        self,
        text: str,
        *,
        base64_attachments: list[str] | None = None,
        link_preview: LinkPreview | None = None,
        mentions: list[dict[str, Any]] | None = None,
        text_mode: str | None = None,
        view_once: bool = False,
    ) -> int:
        return await self.bot.send(
            self.message.recipient(),
            text,
            base64_attachments=base64_attachments,
            mentions=mentions,
            text_mode=text_mode,
            link_preview=link_preview,
            view_once=view_once,
        )

    async def edit(  # noqa: PLR0913
        self,
        text: str,
        edit_timestamp: int,
        *,
        base64_attachments: list[str] | None = None,
        link_preview: LinkPreview | None = None,
        mentions: list[dict[str, Any]] | None = None,
        text_mode: str | None = None,
        view_once: bool = False,
    ) -> int:
        return await self.bot.send(
            self.message.recipient(),
            text,
            base64_attachments=base64_attachments,
            mentions=mentions,
            text_mode=text_mode,
            edit_timestamp=edit_timestamp,
            link_preview=link_preview,
            view_once=view_once,
        )

    async def reply(  # noqa: PLR0913
        self,
        text: str,
        *,
        base64_attachments: list[str] | None = None,
        link_preview: LinkPreview | None = None,
        mentions: (
            list[dict[str, Any]] | None
        ) = None,  # [{ "author": "uuid" , "start": 0, "length": 1 }]
        text_mode: str | None = None,
        view_once: bool = False,
    ) -> int:
        send_mentions = self._convert_receive_mentions_into_send_mentions(
            self.message.mentions,
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
            link_preview=link_preview,
            view_once=view_once,
        )

    async def react(self, emoji: str) -> None:
        await self.bot.react(self.message, emoji)

    async def receipt(self, receipt_type: Literal["read", "viewed"]) -> None:
        await self.bot.receipt(self.message, receipt_type)

    async def start_typing(self) -> None:
        await self.bot.start_typing(self.message.recipient())

    async def stop_typing(self) -> None:
        await self.bot.stop_typing(self.message.recipient())

    async def remote_delete(self, timestamp: int) -> int:
        return await self.bot.remote_delete(
            self.message.recipient(), timestamp=timestamp
        )

    def _convert_receive_mentions_into_send_mentions(
        self,
        mentions: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]] | None:
        if mentions is None:
            return None

        send_mentions = deepcopy(mentions)
        for mention in send_mentions:
            if "author" not in mention:
                mention["author"] = mention["uuid"]
        return send_mentions
