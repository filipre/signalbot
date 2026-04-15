from __future__ import annotations

from pydantic import BaseModel

from signalbot.api.generated_receive.message_envelope_schema import MessageEnvelope


class ReceivedMessage(BaseModel):
    envelope: MessageEnvelope
    account: str
