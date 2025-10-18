from __future__ import annotations

from typing import Any


class Quote:
    def __init__(  # noqa: PLR0913
        self,
        quote_id: int,
        author: str,
        author_number: str,
        author_uuid: str,
        text: str = "",
        attachments: list[dict[str, Any]] | None = None,
    ) -> None:
        self.id = quote_id
        self.author = author
        self.author_number = author_number
        self.author_uuid = author_uuid
        self.text = text
        self.attachments = attachments or []

    @classmethod
    def from_dict(cls, quote_dict: dict[str, Any] | None) -> Quote | None:
        if not quote_dict:
            return None

        try:
            return cls(
                id=quote_dict["id"],
                author=quote_dict["author"],
                author_number=quote_dict["authorNumber"],
                author_uuid=quote_dict["authorUuid"],
                text=quote_dict.get("text", ""),
                attachments=quote_dict.get("attachments", []),
            )
        except (KeyError, TypeError):
            return None
