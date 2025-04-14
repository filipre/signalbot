import base64

import aiohttp
import websockets
from typing import Any, Optional


class SignalAPI:
    def __init__(
        self,
        signal_service: str,
        phone_number: str,
    ):
        self.signal_service = signal_service
        self.phone_number = phone_number

        # self.session = aiohttp.ClientSession()

    async def receive(self):
        try:
            uri = self._receive_ws_uri()
            self.connection = websockets.connect(uri, ping_interval=None)
            async with self.connection as websocket:
                async for raw_message in websocket:
                    yield raw_message

        except Exception as e:
            raise ReceiveMessagesError(e)

    async def send(
        self,
        receiver: str,
        message: str,
        base64_attachments: list = None,
        quote_author: str = None,
        quote_mentions: list = None,
        quote_message: str = None,
        quote_timestamp: str = None,
        mentions: list[dict[str, Any]] | None = None,
        text_mode: str = None,
    ) -> aiohttp.ClientResponse:
        uri = self._send_rest_uri()
        if base64_attachments is None:
            base64_attachments = []

        payload = {
            "base64_attachments": base64_attachments,
            "message": message,
            "number": self.phone_number,
            "recipients": [receiver],
        }

        if quote_author:
            payload["quote_author"] = quote_author
        if quote_mentions:
            payload["quote_mentions"] = quote_mentions
        if quote_message:
            payload["quote_message"] = quote_message
        if quote_timestamp:
            payload["quote_timestamp"] = quote_timestamp
        if mentions:
            payload["mentions"] = mentions
        if text_mode:
            payload["text_mode"] = text_mode

        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.post(uri, json=payload)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
            KeyError,
        ):
            raise SendMessageError

    async def react(
        self, recipient: str, reaction: str, target_author: str, timestamp: int
    ) -> aiohttp.ClientResponse:
        uri = self._react_rest_uri()
        payload = {
            "recipient": recipient,
            "reaction": reaction,
            "target_author": target_author,
            "timestamp": timestamp,
        }
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.post(uri, json=payload)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise ReactionError

    async def start_typing(self, receiver: str):
        uri = self._typing_indicator_uri()
        payload = {
            "recipient": receiver,
        }
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.put(uri, json=payload)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise StartTypingError

    async def stop_typing(self, receiver: str):
        uri = self._typing_indicator_uri()
        payload = {
            "recipient": receiver,
        }
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.delete(uri, json=payload)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise StopTypingError

    async def get_groups(self) -> list[dict[str, Any]]:
        uri = self._groups_uri()
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(uri)
                resp.raise_for_status()
                return await resp.json()
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise GroupsError

    async def get_attachment(self, attachment_id: str) -> str:
        uri = f"{self._attachment_rest_uri()}/{attachment_id}"
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(uri)
                resp.raise_for_status()
                content = await resp.content.read()
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise GetAttachmentError

        base64_bytes = base64.b64encode(content)
        base64_string = str(base64_bytes, encoding="utf-8")

        return base64_string

    async def delete_attachment(self, attachment_id: str) -> str:
        uri = f"{self._attachment_rest_uri()}/{attachment_id}"
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.delete(uri)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise GetAttachmentError

    async def update_contact(
        self,
        receiver: str,
        expiration_in_seconds: Optional[int] = None,
        name: Optional[str] = None,
    ) -> None:
        uri = self._contacts_uri()
        payload = {"recipient": receiver}

        if expiration_in_seconds is not None:
            payload["expiration_in_seconds"] = expiration_in_seconds

        if name is not None:
            payload["name"] = name

        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.put(uri, json=payload)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise ContactUpdateError

    async def update_group(
        self,
        group_id: str,
        base64_avatar: Optional[str] = None,
        description: Optional[str] = None,
        expiration_in_seconds: Optional[int] = None,
        name: Optional[str] = None,
    ) -> None:
        uri = self._group_id_uri(group_id)
        payload = {}

        if base64_avatar is not None:
            payload["base64_avatar"] = base64_avatar

        if description is not None:
            payload["description"] = description

        if expiration_in_seconds is not None:
            payload["expiration_time"] = expiration_in_seconds

        if name is not None:
            payload["name"] = name

        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.put(uri, json=payload)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise ContactUpdateError

    def _attachment_rest_uri(self):
        return f"http://{self.signal_service}/v1/attachments"

    def _receive_ws_uri(self):
        return f"ws://{self.signal_service}/v1/receive/{self.phone_number}"

    def _send_rest_uri(self):
        return f"http://{self.signal_service}/v2/send"

    def _react_rest_uri(self):
        return f"http://{self.signal_service}/v1/reactions/{self.phone_number}"

    def _typing_indicator_uri(self):
        return f"http://{self.signal_service}/v1/typing-indicator/{self.phone_number}"

    def _groups_uri(self):
        return f"http://{self.signal_service}/v1/groups/{self.phone_number}"

    def _group_id_uri(self, group_id: str):
        return self._groups_uri() + "/" + group_id

    def _contacts_uri(self):
        return f"http://{self.signal_service}/v1/contacts/{self.phone_number}"


class ReceiveMessagesError(Exception):
    pass


class SendMessageError(Exception):
    pass


class TypingError(Exception):
    pass


class StartTypingError(TypingError):
    pass


class StopTypingError(TypingError):
    pass


class ReactionError(Exception):
    pass


class GroupsError(Exception):
    pass


class GetAttachmentError(Exception):
    pass


class ContactUpdateError(Exception):
    pass
