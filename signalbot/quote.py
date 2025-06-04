from typing import Optional, List, Dict, Any


class Quote:
    
    def __init__(
        self,
        id: int,
        author: str,
        author_number: str,
        author_uuid: str,
        text: str = "",
        attachments: List[Dict[str, Any]] = None,
    ):
        self.id = id
        self.author = author
        self.author_number = author_number
        self.author_uuid = author_uuid
        self.text = text
        self.attachments = attachments or []

    @classmethod
    def from_dict(cls, quote_dict: Optional[Dict[str, Any]]) -> Optional["Quote"]:
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