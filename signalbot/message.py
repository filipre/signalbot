import json
from enum import Enum


class MessageType(Enum):
    SYNC_MESSAGE = 1
    DATA_MESSAGE = 2


class Message:
    def __init__(
        self,
        source: str,
        timestamp: int,
        type: MessageType,
        text: str,
        base64_attachments: list = None,
        group: str = None,
        reaction: str = None,
        raw_message: str = None,
    ):
        # required
        self.source = source
        self.timestamp = timestamp
        self.type = type
        self.text = text
        # optional
        if base64_attachments is None:
            self.base64_attachments = []
        self.group = group
        self.reaction = reaction

        self.raw_message = raw_message

    @classmethod
    def parse(cls, raw_message: str):
        try:
            raw_message = json.loads(raw_message)
        except Exception:
            raise UnknownMessageFormatError

        # General attributes
        try:
            source = raw_message["envelope"]["source"]
            timestamp = raw_message["envelope"]["timestamp"]
        except Exception:
            raise UnknownMessageFormatError

        # Option 1: syncMessage
        if "syncMessage" in raw_message["envelope"]:
            type = MessageType.SYNC_MESSAGE
            text = cls._parse_sync_message(raw_message["envelope"]["syncMessage"])
            group = cls._parse_group_information(
                raw_message["envelope"]["syncMessage"]["sentMessage"]
            )
            reaction = cls._parse_reaction(
                raw_message["envelope"]["syncMessage"]["sentMessage"]
            )

        # Option 2: dataMessage
        elif "dataMessage" in raw_message["envelope"]:
            type = MessageType.DATA_MESSAGE
            text = cls._parse_data_message(raw_message["envelope"]["dataMessage"])
            group = cls._parse_group_information(raw_message["envelope"]["dataMessage"])
            reaction = cls._parse_reaction(raw_message["envelope"]["dataMessage"])

        else:
            raise UnknownMessageFormatError

        # TODO: base64_attachments
        base64_attachments = []

        return cls(source, timestamp, type, text, base64_attachments, group, reaction)

    @classmethod
    def _parse_sync_message(cls, sync_message: dict) -> str:
        try:
            text = sync_message["sentMessage"]["message"]
            return text
        except Exception:
            raise UnknownMessageFormatError

    @classmethod
    def _parse_data_message(cls, data_message: dict) -> str:
        try:
            text = data_message["message"]
            return text
        except Exception:
            raise UnknownMessageFormatError

    @classmethod
    def _parse_group_information(self, message: dict) -> str:
        try:
            group = message["groupInfo"]["groupId"]
            return group
        except Exception:
            return None

    @classmethod
    def _parse_reaction(self, message: dict) -> str:
        try:
            reaction = message["reaction"]["emoji"]
            return reaction
        except Exception:
            return None

    def __str__(self):
        if self.text is None:
            return ""
        return self.text


class UnknownMessageFormatError(Exception):
    pass
