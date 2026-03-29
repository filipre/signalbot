from __future__ import annotations

from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    server_delivered_timestamp: int
    server_received_timestamp: int
    source: str | None = Field(None, deprecated=True)
    source_device: int | None = None
    source_name: str | None = None
    source_number: str | None = None
    source_uuid: str | None = None
    timestamp: int
