from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from signalbot.link_previews import LinkPreview
from signalbot.quote import Quote

if TYPE_CHECKING:
    from signalbot.api import SignalAPI


class MessageType(Enum):
    SYNC_MESSAGE = 1  # Message received in a linked device
    DATA_MESSAGE = 2  # Message received in a primary device
    EDIT_MESSAGE = 3  # Message received is an edit of a previous message
    DELETE_MESSAGE = 4  # Message received is a remote delete of a previous message
    READ_MESSAGE = 5  # User read some messages


@dataclass
class Message:
    # required
    source: str
    source_number: str | None
    source_uuid: str
    timestamp: int
    type: MessageType
    text: str
    # optional
    base64_attachments: list[str] = field(default_factory=list)
    attachments_local_filenames: list[str] = field(default_factory=list)
    view_once: bool = False
    link_previews: list[LinkPreview] = field(default_factory=list)
    group: str | None = None
    reaction: str | None = None
    mentions: list[str] = field(default_factory=list)
    quote: Quote | None = None
    read_messages: list[dict] | None = None
    target_sent_timestamp: int | None = None
    remote_delete_timestamp: int | None = None
    raw_message: str | None = None

    def recipient(self) -> str:
        # Case 1: Group chat
        if self.group:
            return self.group  # internal ID

        # Case 2: User chat
        return self.source

    def is_private(self) -> bool:
        return not bool(self.group)

    def is_group(self) -> bool:
        return bool(self.group)

    @classmethod
    def _extract_message_data(
        cls, envelope: dict
    ) -> tuple[MessageType, dict, int | None, int | None]:
        """Extract message type, data_message, and timestamps from envelope."""
        target_sent_timestamp = None

        if "syncMessage" in envelope:
            sync_message = envelope["syncMessage"]
            if sync_message == {}:
                raise UnknownMessageFormatError

            if "readMessages" in sync_message:
                message_type = MessageType.READ_MESSAGE
                data_message = {
                    "message": "",
                    "readMessages": sync_message["readMessages"],
                }
            else:
                message_type = MessageType.SYNC_MESSAGE
                data_message = sync_message["sentMessage"]

            if "editMessage" in data_message:
                message_type = MessageType.EDIT_MESSAGE
                target_sent_timestamp = data_message["editMessage"][
                    "targetSentTimestamp"
                ]
                data_message = data_message["editMessage"]["dataMessage"]

        elif "dataMessage" in envelope:
            message_type = MessageType.DATA_MESSAGE
            data_message = envelope["dataMessage"]

        elif "editMessage" in envelope:
            message_type = MessageType.EDIT_MESSAGE
            data_message = envelope["editMessage"]["dataMessage"]
            target_sent_timestamp = envelope["editMessage"]["targetSentTimestamp"]

        else:
            raise UnknownMessageFormatError

        remote_delete_timestamp = None
        if "remoteDelete" in data_message:
            message_type = MessageType.DELETE_MESSAGE
            remote_delete_timestamp = data_message["remoteDelete"]["timestamp"]

        return (
            message_type,
            data_message,
            target_sent_timestamp,
            remote_delete_timestamp,
        )

    @classmethod
    async def parse(cls, signal: SignalAPI, raw_message_str: str) -> Message:
        try:
            raw_message = json.loads(raw_message_str)
        except Exception as exc:
            raise UnknownMessageFormatError from exc

        envelope = raw_message["envelope"]
        # General attributes
        try:
            source = envelope["source"]
            source_uuid = envelope["sourceUuid"]
            timestamp = envelope["timestamp"]
        except Exception as exc:
            raise UnknownMessageFormatError from exc

        source_number = envelope.get("sourceNumber")

        message_type, data_message, target_sent_timestamp, remote_delete_timestamp = (
            cls._extract_message_data(envelope)
        )

        text = cls._parse_data_message(data_message)
        group = cls._parse_group_information(data_message)
        reaction = cls._parse_reaction(data_message)
        mentions = cls._parse_mentions(data_message)
        quote = cls._parse_quote(data_message)
        read_messages = data_message.get("readMessages")

        base64_attachments, attachments_local_filenames, link_previews = [], [], []
        view_once = False
        if signal.download_attachments:
            base64_attachments = await cls._parse_attachments(signal, data_message)
            attachments_local_filenames = cls._parse_attachments_local_filenames(
                data_message,
            )
            link_previews = await cls._parse_previews(signal, data_message)
            view_once = data_message.get("viewOnce", False)

        return cls(
            source,
            source_number,
            source_uuid,
            timestamp,
            message_type,
            text,
            base64_attachments=base64_attachments,
            attachments_local_filenames=attachments_local_filenames,
            view_once=view_once,
            link_previews=link_previews,
            group=group,
            reaction=reaction,
            mentions=mentions,
            quote=quote,
            read_messages=read_messages,
            target_sent_timestamp=target_sent_timestamp,
            remote_delete_timestamp=remote_delete_timestamp,
            raw_message=raw_message_str,
        )

    @classmethod
    async def _parse_attachments(cls, signal: SignalAPI, data_message: dict) -> str:
        if "attachments" not in data_message:
            return []

        return [
            await signal.get_attachment(attachment["id"])
            for attachment in data_message["attachments"]
        ]

    @classmethod
    def _parse_attachments_local_filenames(cls, data_message: dict) -> list[str]:
        if "attachments" not in data_message:
            return []

        # The ["id"] is the local filename and the ["filename"] is the remote filename
        return [attachment["id"] for attachment in data_message["attachments"]]

    @classmethod
    def _parse_data_message(cls, data_message: dict) -> str:
        try:
            return data_message["message"]
        except KeyError as exc:
            raise UnknownMessageFormatError from exc

    @classmethod
    def _parse_group_information(cls, message: dict) -> str:
        try:
            return message["groupInfo"]["groupId"]
        except KeyError:
            return None

    @classmethod
    def _parse_mentions(cls, data_message: dict) -> list:
        try:
            return data_message["mentions"]
        except KeyError:
            return []

    @classmethod
    def _parse_reaction(cls, message: dict) -> str:
        try:
            return message["reaction"]["emoji"]
        except KeyError:
            return None

    @classmethod
    def _parse_quote(cls, message: dict) -> Quote | None:
        try:
            return Quote.model_validate(message["quote"])
        except KeyError:
            return None

    def __str__(self) -> str:
        if self.text is None:
            return ""
        return self.text

    @classmethod
    async def _parse_previews(cls, signal: SignalAPI, data_message: dict) -> list:
        parsed_previews = []
        try:
            for preview in data_message["previews"]:
                base64_thumbnail = await signal.get_attachment(preview["image"]["id"])
                parsed_previews.append(
                    LinkPreview(
                        base64_thumbnail=base64_thumbnail,
                        title=preview["title"],
                        description=preview["description"],
                        url=preview["url"],
                        id=preview["image"]["id"],
                    ),
                )
        except KeyError:
            return []

        return parsed_previews


class UnknownMessageFormatError(Exception):
    pass
