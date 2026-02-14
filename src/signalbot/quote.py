from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Quote(BaseModel):
    """Dataclass to representing a quote.

    Attributes:
        id: The ID of the quoted message.
        author: The author of the quoted message.
        author_number: The phone number of the author of the quoted message, if
            available.
        author_uuid: The UUID of the author of the quoted message.
        text: The text of the quoted message.
        attachments: A list of attachments of the quoted message, if available.
    """

    model_config = ConfigDict(alias_generator=to_camel)  # Support fields in camel case

    id: int
    author: str
    author_number: str | None = None
    author_uuid: str
    text: str
    attachments: list[dict[str, Any]]
