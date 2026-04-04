from __future__ import annotations

from signalbot.api.generated_receive.preview_schema import Preview as BasePreview


class Preview(BasePreview):
    base64_thumbnail: str | None = None
