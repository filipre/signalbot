from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Reaction(BaseModel):
    """Dataclass representing a reaction.

    Attributes:
        emoji: The emoji of the reaction.
        target_author: The author of the target message.
        target_author_number: The phone number of the author of the target message, if
            available.
        target_author_uuid: The UUID of the author of the target message.
        target_sent_timestamp: The timestamp of the target message.
        is_remove: Whether this reaction is a removal of a previous reaction.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    emoji: str
    target_author: str
    target_author_number: str | None = None
    target_author_uuid: str
    target_sent_timestamp: int
    is_remove: bool = False
