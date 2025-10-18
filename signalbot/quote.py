from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Quote(BaseModel):
    # Support fields in camel case
    model_config = ConfigDict(alias_generator=to_camel)

    id: int
    author: str
    author_number: str
    author_uuid: str
    text: str = ""
    attachments: list[dict[str, Any]] = []
