from __future__ import annotations

from pydantic import BaseModel


class LinkPreview(BaseModel):
    """Dataclass to representing a link preview.

    Attributes:
        base64_thumbnail: The base64 encoded thumbnail of the link preview, if
            available.
        title: The title of the link preview.
        description: The description of the link preview, if available.
        url: The url of the link preview.
        id: The local filename for a received link preview.
    """

    base64_thumbnail: str | None
    title: str
    description: str | None
    url: str
    id: str | None = None
