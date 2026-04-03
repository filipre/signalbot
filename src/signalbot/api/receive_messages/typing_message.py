from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from signalbot.api.receive_messages import BaseMessage

if TYPE_CHECKING:
    from signalbot.api.generated_receive import (
        MessageEnvelope,
    )
    from signalbot.api.generated_receive import TypingMessage as BaseTypingMessage


class TypingAction(StrEnum):
    STARTED = "STARTED"
    STOPPED = "STOPPED"


class TypingMessage(BaseMessage):
    action: TypingAction
    group_id: str | None = None
    timestamp: int

    @classmethod
    async def _internal_parse(
        cls,
        message_envelope: MessageEnvelope,
        typing_message: BaseTypingMessage,
    ) -> TypingMessage:
        if typing_message.action is None:
            error_msg = "TypingMessage is missing required field: action"
            raise ValueError(error_msg)

        return TypingMessage(
            server_delivered_timestamp=message_envelope.server_delivered_timestamp,
            server_received_timestamp=message_envelope.server_received_timestamp,
            source=message_envelope.source,
            source_device=message_envelope.source_device,
            source_name=message_envelope.source_name,
            source_number=message_envelope.source_number,
            source_uuid=message_envelope.source_uuid,
            timestamp=typing_message.timestamp,
            group_id=typing_message.group_id,
            action=TypingAction(typing_message.action),
        )

    @classmethod
    async def from_message_envelope(
        cls, message_envelope: MessageEnvelope
    ) -> TypingMessage:
        if message_envelope.typing_message is not None:
            return await cls._internal_parse(
                message_envelope,
                message_envelope.typing_message,
            )

        error_msg = "MessageEnvelope does not contain a TypingMessage"
        raise ValueError(error_msg)

    def is_group(self) -> bool:

        return self.group_id is not None

    def is_private(self) -> bool:

        return not self.is_group()

    def source_or_group_uuid(self) -> str:
        if self.group_id is not None:
            return self.group_id

        if self.source_uuid is not None:
            return self.source_uuid

        if self.source_number is not None:
            return self.source_number

        error_msg = "Message does not contain a source"
        raise ValueError(error_msg)
