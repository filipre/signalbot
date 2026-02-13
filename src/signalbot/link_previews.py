from __future__ import annotations

from pydantic import BaseModel


class LinkPreview(BaseModel):
    """Dataclass to hold a link preview."""

    base64_thumbnail: str | None
    """The base64 encoded thumbnail of the link preview, if available."""

    title: str
    """The title of the link preview."""

    description: str | None
    """The description of the link preview, if available."""

    url: str
    """The url of the link preview."""

    id: str | None = None
    """This is the local filename for a received link preview."""
