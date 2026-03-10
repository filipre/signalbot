from __future__ import annotations

import base64
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel

from signalbot.api.messages.base_message import BaseMessage
from signalbot.api.py_schema.attachment_schema import Attachment as BaseAttachment
from signalbot.api.py_schema.preview_schema import Preview as BasePreview

if TYPE_CHECKING:
    from signalbot.api import SignalAPI
    from signalbot.api.py_schema.data_message_schema import (
        DataMessage as DataMessageBase,
    )
    from signalbot.api.py_schema.group_info_schema import GroupInfo
    from signalbot.api.py_schema.mention_schema import Mention
    from signalbot.api.py_schema.message_envelope_schema import MessageEnvelope
    from signalbot.api.py_schema.quote_schema import Quote
    from signalbot.api.py_schema.reaction_schema import Reaction
    from signalbot.api.py_schema.sticker_schema import Sticker
    from signalbot.api.py_schema.sync_data_message_schema import SyncDataMessage
    from signalbot.api.py_schema.text_style_schema import TextStyle


class Preview(BasePreview):
    base64_thumbnail: str | None = None


class Attachment(BaseAttachment):
    base64_content: str | None = None


class ReceiveDataMessage(BaseMessage):
    group_info: GroupInfo | None = None
    attachments: list[Attachment] | None = None
    expires_in_seconds: int | None = None
    mentions: list[Mention] | None = None
    message: str | None = None
    previews: list[Preview] | None = None
    base64_previews: list[str] | None = None
    quote: Quote | None = None
    reaction: Reaction | None = None
    sticker: Sticker | None = None
    text_styles: list[TextStyle] | None = None
    timestamp: int
    view_once: bool | None = None

    @classmethod
    async def _download_attachments(
        cls, signal: SignalAPI, attachments: list[Attachment]
    ) -> list[str | None]:
        return [
            await signal.get_attachment(attachment.id)
            if attachment.id is not None
            else None
            for attachment in attachments
        ]

    @classmethod
    async def _download_thumbnails(
        cls, signal: SignalAPI, link_previews: list[Preview]
    ) -> list[str | None]:
        return [
            await signal.get_attachment(link_preview.image.id)
            if link_preview.image is not None and link_preview.image.id is not None
            else None
            for link_preview in link_previews
        ]

    @classmethod
    async def _internal_parse(
        cls,
        message_envelope: MessageEnvelope,
        data_message: DataMessageBase | SyncDataMessage,
        signal: SignalAPI,
    ) -> ReceiveDataMessage:
        attachments = None
        if data_message.attachments is not None:
            attachments = [
                Attachment.model_validate(attachment.model_dump())
                for attachment in data_message.attachments
            ]

        link_previews = None
        if data_message.previews is not None:
            link_previews = [
                Preview.model_validate(preview.model_dump())
                for preview in data_message.previews
            ]

        received_data_message = ReceiveDataMessage(
            server_delivered_timestamp=message_envelope.server_delivered_timestamp,
            server_received_timestamp=message_envelope.server_received_timestamp,
            source=message_envelope.source,
            source_device=message_envelope.source_device,
            source_name=message_envelope.source_name,
            source_number=message_envelope.source_number,
            source_uuid=message_envelope.source_uuid,
            group_info=data_message.group_info,
            timestamp=data_message.timestamp,
            attachments=attachments,
            expires_in_seconds=data_message.expires_in_seconds,
            mentions=data_message.mentions,
            message=data_message.message,
            previews=link_previews,
            quote=data_message.quote,
            reaction=data_message.reaction,
            sticker=data_message.sticker,
            text_styles=data_message.text_styles,
            view_once=data_message.view_once,
        )

        if (
            received_data_message.attachments is not None
            and signal.download_attachments
        ):
            base64_contents = await cls._download_attachments(
                signal, received_data_message.attachments
            )
            for i, base64_content in enumerate(base64_contents):
                received_data_message.attachments[i].base64_content = base64_content

        if received_data_message.previews is not None and signal.download_attachments:
            base64_contents = await cls._download_thumbnails(
                signal, received_data_message.previews
            )
            for i, base64_content in enumerate(base64_contents):
                received_data_message.previews[i].base64_thumbnail = base64_content

        return received_data_message

    @classmethod
    async def from_message_envelope(
        cls, message_envelope: MessageEnvelope, signal: SignalAPI
    ) -> ReceiveDataMessage:
        data_message = message_envelope.data_message
        if data_message is None:
            error_msg = "MessageEnvelope does not contain a DataMessage"
            raise ValueError(error_msg)

        return await cls._internal_parse(message_envelope, data_message, signal)

    @classmethod
    async def from_message_envelope_sync_message(
        cls, message_envelope: MessageEnvelope, signal: SignalAPI
    ) -> ReceiveDataMessage:
        if message_envelope.sync_message is None:
            error_msg = "MessageEnvelope does not contain a SyncMessage"
            raise ValueError(error_msg)

        data_message = message_envelope.sync_message.sent_message
        if data_message is None:
            error_msg = "SyncMessage does not contain a SentMessage"
            raise ValueError(error_msg)

        return await cls._internal_parse(message_envelope, data_message, signal)

    def is_group(self) -> bool:
        """Check if the message is a group message.

        Returns:
            True if the message is a group message, False otherwise.
        """
        return self.group_info is not None and self.group_info.group_id is not None

    def is_private(self) -> bool:
        """Check if the message is a private (one-on-one) message.


        Returns:
            True if the message is a private (one-on-one) message, False otherwise.
        """
        return not self.is_group()

    def to_send_message(self, recipients: list[str]) -> SendDataMessage:
        """Convert the received message to a SendDataMessage that can be sent using the
            API.

        Returns:
            A SendDataMessage object that can be sent using the API.
        """
        base_64_attachments = None
        if self.attachments is not None:
            base_64_attachments = []
            for attachment in self.attachments:
                if attachment.base64_content is None:
                    if attachment.id is None:
                        error_msg = (
                            "Attachment does not contain an id or base64 content"
                        )
                        raise ValueError(error_msg)

                    with Path(attachment.id).open("rb") as f:
                        base64_content = str(
                            base64.b64encode(f.read()), encoding="utf-8"
                        )
                else:
                    base64_content = attachment.base64_content
                base_64_attachments.append(base64_content)

        return SendDataMessage(
            recipients=recipients,
            base64_attachments=base_64_attachments,
            expires_in_seconds=self.expires_in_seconds,
            mentions=self.mentions,
            message=self.message,
            previews=self.previews,
            quote=self.quote,
            reaction=self.reaction,
            sticker=self.sticker,
            text_styles=self.text_styles,
            view_once=self.view_once,
        )


class SendDataMessage(BaseModel):
    recipients: list[str]
    base64_attachments: list[str] | None = None
    expires_in_seconds: int | None = None
    mentions: list[Mention] | None = None
    message: str | None = None
    previews: list[Preview] | None = None
    quote: Quote | None = None
    reaction: Reaction | None = None
    sticker: Sticker | None = None
    text_styles: list[TextStyle] | None = None
    view_once: bool | None = None
