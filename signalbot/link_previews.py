from __future__ import annotations

from pydantic import BaseModel


class LinkPreview(BaseModel):
    base64_thumbnail: str
    title: str
    description: str | None = None
    url: str

    #  This is the local filename for a received link preview
    id: str | None = None
