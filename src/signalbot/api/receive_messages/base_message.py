from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from signalbot.api.generated_receive import GroupInfo


class BaseMessage(ABC, BaseModel):
    server_delivered_timestamp: int
    server_received_timestamp: int
    source: str | None = Field(default=None, deprecated=True)
    source_device: int | None = None
    source_name: str | None = None
    source_number: str | None = None
    source_uuid: str | None = None
    timestamp: int

    @abstractmethod
    def is_group(self) -> bool:
        pass

    @abstractmethod
    def is_private(self) -> bool:
        pass

    @abstractmethod
    def source_or_group_uuid(self) -> str:
        pass


class BaseMessageWithGroup(BaseMessage):
    group_info: GroupInfo | None = None

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

    def source_or_group_uuid(self) -> str:
        """Get the source of the message.

        Returns:
            The source of the message.
        """
        if self.group_info is not None and self.group_info.group_id is not None:
            return self.group_info.group_id

        if self.source_uuid is not None:
            return self.source_uuid

        if self.source_number is not None:
            return self.source_number

        error_msg = "Message does not contain a source"
        raise ValueError(error_msg)
