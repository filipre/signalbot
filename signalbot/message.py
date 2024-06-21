import json
from enum import Enum


from signalbot.api import SignalAPI


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
        attachments_filenames: Optional[list] = None,
        group: str = None,
        reaction: str = None,
        mentions: list = None,
        raw_message: str = None,
    ):
        # required
        self.source = source
        self.timestamp = timestamp
        self.type = type
        self.text = text

        # optional
        self.base64_attachments = base64_attachments
        if self.base64_attachments is None:
            self.base64_attachments = []

        self.attachments_filenames = attachments_filenames
        if self.attachments_filenames is None:
            self.attachments_filenames = []

        self.group = group

        self.reaction = reaction

        self.mentions = mentions
        if self.mentions is None:
            self.mentions = []

        self.raw_message = raw_message

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
    async def parse(cls, signal: SignalAPI, raw_message: str):
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
            mentions = cls._parse_mentions(
                raw_message["envelope"]["syncMessage"]["sentMessage"]
            )
            base64_attachments = None

        # Option 2: dataMessage
        elif "dataMessage" in raw_message["envelope"]:
            type = MessageType.DATA_MESSAGE
            text = cls._parse_data_message(raw_message["envelope"]["dataMessage"])
            group = cls._parse_group_information(raw_message["envelope"]["dataMessage"])
            reaction = cls._parse_reaction(raw_message["envelope"]["dataMessage"])
            mentions = cls._parse_mentions(raw_message["envelope"]["dataMessage"])
            base64_attachments = await cls._parse_attachments(
                signal, raw_message["envelope"]["dataMessage"]
            )
            attachments_filenames = cls._parse_attachments_filenames(raw_message["envelope"]["dataMessage"])

        else:
            raise UnknownMessageFormatError

        return cls(
            source,
            timestamp,
            type,
            text,
            base64_attachments,
            attachments_filenames,
            group,
            reaction,
            mentions,
            raw_message,
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
    def _parse_attachments_filenames(cls, data_message: dict) -> list[str]:

        if "attachments" not in data_message:
            return []

        return [attachment["id"] for attachment in data_message["attachments"]]
    
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
    def _parse_mentions(cls, data_message: dict) -> list:
        try:
            mentions = data_message["mentions"]
            return mentions
        except Exception:
            return []

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
