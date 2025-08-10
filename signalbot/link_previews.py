from pydantic import BaseModel


class LinkPreview(BaseModel):
    base64_thumbnail: str
    title: str
    description: str
    url: str
