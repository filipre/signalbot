from pydantic import BaseModel


class LinkPreview(BaseModel):
    base64_thumbnail: str
    title: str
    description: str
    url: str
    id: str | None = None  #  This is the local filename for a received link preview
