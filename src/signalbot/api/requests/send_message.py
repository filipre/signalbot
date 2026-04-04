from __future__ import annotations

from copy import deepcopy

from signalbot.api.generated import SendMessageV2


class SendMessage(SendMessageV2):
    pass


class SentMessage(SendMessage):
    timestamp: int

    @classmethod
    def from_send_message(
        cls, send_message: SendMessage, timestamp: int
    ) -> SentMessage:
        send_message = deepcopy(send_message)
        return cls(
            base64_attachments=send_message.base64_attachments,
            edit_timestamp=send_message.edit_timestamp,
            link_preview=send_message.link_preview,
            mentions=send_message.mentions,
            text=send_message.text,
            notify_self=send_message.notify_self,
            number=send_message.number,
            quote_author=send_message.quote_author,
            quote_mentions=send_message.quote_mentions,
            quote_message=send_message.quote_message,
            quote_timestamp=send_message.quote_timestamp,
            recipients=send_message.recipients,
            sticker=send_message.sticker,
            text_mode=send_message.text_mode,
            view_once=send_message.view_once,
            timestamp=timestamp,
        )
