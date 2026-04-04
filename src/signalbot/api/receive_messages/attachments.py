from __future__ import annotations

from signalbot.api.generated_receive.attachment_schema import (
    Attachment as BaseAttachment,
)


class Attachment(BaseAttachment):
    base64_content: str | None = None
