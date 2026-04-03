from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.api.receive_messages import BaseMessageWithGroup

if TYPE_CHECKING:
    from signalbot.api.generated_receive import (
        DataMessage,
        MessageEnvelope,
        SyncDataMessage,
    )
    from signalbot.api.generated_receive import RemoteDelete as BaseRemoteDelete


class RemoteDelete(BaseMessageWithGroup):
    @classmethod
    async def _internal_parse(
        cls,
        message_envelope: MessageEnvelope,
        data_message: DataMessage | SyncDataMessage,
        remote_delete: BaseRemoteDelete,
    ) -> RemoteDelete:
        return cls(
            server_delivered_timestamp=message_envelope.server_delivered_timestamp,
            server_received_timestamp=message_envelope.server_received_timestamp,
            source=message_envelope.source,
            source_device=message_envelope.source_device,
            source_name=message_envelope.source_name,
            source_number=message_envelope.source_number,
            source_uuid=message_envelope.source_uuid,
            timestamp=remote_delete.timestamp,
            group_info=data_message.group_info,
        )

    @classmethod
    async def from_message_envelope(
        cls, message_envelope: MessageEnvelope
    ) -> RemoteDelete:
        if (
            message_envelope.data_message is not None
            and message_envelope.data_message.remote_delete is not None
        ):
            return await cls._internal_parse(
                message_envelope,
                message_envelope.data_message,
                message_envelope.data_message.remote_delete,
            )

        if (
            message_envelope.sync_message is not None
            and message_envelope.sync_message.sent_message is not None
            and message_envelope.sync_message.sent_message.remote_delete is not None
        ):
            return await cls._internal_parse(
                message_envelope,
                message_envelope.sync_message.sent_message,
                message_envelope.sync_message.sent_message.remote_delete,
            )

        error_msg = "MessageEnvelope does not contain a RemoteDelete"
        raise ValueError(error_msg)
