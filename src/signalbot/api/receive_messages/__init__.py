from signalbot.api.receive_messages.attachments import Attachment
from signalbot.api.receive_messages.base_message import BaseMessage
from signalbot.api.receive_messages.data_message import ReceiveDataMessage
from signalbot.api.receive_messages.group_update_message import GroupUpdateMessage
from signalbot.api.receive_messages.link_previews import Preview
from signalbot.api.receive_messages.received_message import ReceivedMessage
from signalbot.api.receive_messages.remote_delete import RemoteDelete
from signalbot.api.receive_messages.typing_message import TypingMessage

ReceivedMessageType = (
    ReceiveDataMessage | GroupUpdateMessage | RemoteDelete | TypingMessage
)

__all__ = [
    "Attachment",
    "BaseMessage",
    "GroupUpdateMessage",
    "Preview",
    "ReceiveDataMessage",
    "ReceivedMessage",
    "ReceivedMessageType",
    "RemoteDelete",
    "TypingMessage",
]
