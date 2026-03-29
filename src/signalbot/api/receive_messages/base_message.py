from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class BaseMessage(ABC, BaseModel):
    server_delivered_timestamp: int
    server_received_timestamp: int
    source: str | None = Field(None, deprecated=True)
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
