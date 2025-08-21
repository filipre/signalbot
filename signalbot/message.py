from __future__ import annotations

import json
from enum import Enum

from signalbot.api import SignalAPI  # noqa: TC001
from signalbot.link_previews import LinkPreview


class MessageType(Enum):
    SYNC_MESSAGE = 1
    DATA_MESSAGE = 2
    EDIT_MESSAGE = 3


class Message:
    def __init__(  # noqa: ANN204, PLR0913
        self,
        source: str,
        source_number: str | None,
        source_uuid: str,
        timestamp: int,
        type: MessageType,  # noqa: A002
        text: str,
        base64_attachments: list[str] | None = None,
        attachments_local_filenames: list[str] | None = None,
        link_previews: list[LinkPreview] | None = None,
        group: str | None = None,
        reaction: str | None = None,
        mentions: list[str] | None = None,
        target_sent_timestamp: int | None = None,
        raw_message: str | None = None,
    ):
        # required
        self.source = source
        self.source_number = source_number
        self.source_uuid = source_uuid
        self.timestamp = timestamp
        self.type = type
        self.text = text

        # optional
        self.base64_attachments = base64_attachments
        if self.base64_attachments is None:
            self.base64_attachments = []

        self.attachments_local_filenames = attachments_local_filenames
        if self.attachments_local_filenames is None:
            self.attachments_local_filenames = []

        self.group = group

        self.reaction = reaction

        self.mentions = mentions
        if self.mentions is None:
            self.mentions = []

        self.raw_message = raw_message

        self.link_previews = link_previews
        if self.link_previews is None:
            self.link_previews = []

        self.target_sent_timestamp = target_sent_timestamp

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
    async def parse(cls, signal: SignalAPI, raw_message_str: str) -> Message:
        try:
            raw_message = json.loads(raw_message_str)
        except Exception:  # noqa: BLE001
            raise UnknownMessageFormatError  # noqa: B904

        envelope = raw_message["envelope"]
        # General attributes
        try:
            source = envelope["source"]
            source_uuid = envelope["sourceUuid"]
            timestamp = envelope["timestamp"]
        except Exception:  # noqa: BLE001
            raise UnknownMessageFormatError  # noqa: B904

        source_number = envelope.get("sourceNumber")

        target_sent_timestamp = None
        base64_attachments, attachments_local_filenames, link_previews = [], [], []

        if (
            "syncMessage" in envelope
            or "dataMessage" in envelope
            or "editMessage" in envelope
        ):
            if "syncMessage" in envelope:
                type = MessageType.SYNC_MESSAGE  # noqa: A001
                dataMessage = envelope["syncMessage"]["sentMessage"]  # noqa: N806
            elif "dataMessage" in envelope:
                type = MessageType.DATA_MESSAGE  # noqa: A001
                dataMessage = envelope["dataMessage"]  # noqa: N806
            elif "editMessage" in envelope:
                type = MessageType.EDIT_MESSAGE  # noqa: A001
                dataMessage = envelope["editMessage"]["dataMessage"]  # noqa: N806
                target_sent_timestamp = envelope["editMessage"]["targetSentTimestamp"]
            else:
                raise UnknownMessageFormatError

            text = cls._parse_data_message(dataMessage)
            group = cls._parse_group_information(dataMessage)
            reaction = cls._parse_reaction(dataMessage)
            mentions = cls._parse_mentions(dataMessage)
            if signal.download_attachments:
                base64_attachments = await cls._parse_attachments(signal, dataMessage)
                attachments_local_filenames = cls._parse_attachments_local_filenames(
                    dataMessage,
                )
                link_previews = await cls._parse_previews(signal, dataMessage)
        else:
            raise UnknownMessageFormatError

        return cls(
            source,
            source_number,
            source_uuid,
            timestamp,
            type,
            text,
            base64_attachments,
            attachments_local_filenames,
            link_previews,
            group,
            reaction,
            mentions,
            target_sent_timestamp,
            raw_message_str,
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
            text = data_message["message"]
            return text  # noqa: RET504, TRY300
        except Exception:  # noqa: BLE001
            raise UnknownMessageFormatError  # noqa: B904

    @classmethod
    def _parse_group_information(cls, message: dict) -> str:
        try:
            group = message["groupInfo"]["groupId"]
            return group  # noqa: RET504, TRY300
        except Exception:  # noqa: BLE001
            return None

    @classmethod
    def _parse_mentions(cls, data_message: dict) -> list:
        try:
            mentions = data_message["mentions"]
            return mentions  # noqa: RET504, TRY300
        except Exception:  # noqa: BLE001
            return []

    @classmethod
    def _parse_reaction(self, message: dict) -> str:  # noqa: N804
        try:
            reaction = message["reaction"]["emoji"]
            return reaction  # noqa: RET504, TRY300
        except Exception:  # noqa: BLE001
            return None

    def __str__(self):  # noqa: ANN204
        if self.text is None:
            return ""
        return self.text

    @classmethod
    async def _parse_previews(cls, signal: SignalAPI, data_message: dict) -> list:
        try:
            parsed_previews = []
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
            return parsed_previews  # noqa: TRY300
        except Exception:  # noqa: BLE001
            return []


class UnknownMessageFormatError(Exception):
    pass
