import functools
import json
import time
import uuid
from types import MappingProxyType
from unittest.mock import AsyncMock, MagicMock

import aiohttp
from pytest_mock import MockerFixture

from signalbot.bot import Command, Context, SignalBot


def mock_chat(*messages: str):  # noqa: ANN201
    def decorator_chat(func):  # noqa: ANN001, ANN202
        @functools.wraps(func)
        async def wrapper_chat(self, mocker: MockerFixture, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
            mocker.patch("signalbot.SignalAPI.react", new_callable=ReactMessageMock)
            mocker.patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
            receive_mock = mocker.patch(
                "signalbot.SignalAPI.receive",
                new_callable=ReceiveMessagesMock,
            )
            mocker.patch(
                "signalbot.SignalAPI.get_groups",
                new_callable=GetGroupsMock,
            )

            receive_mock.define(messages)
            await self.signal_bot._detect_groups()  # noqa: SLF001
            await self.signal_bot._resolve_commands()  # noqa: SLF001
            await self.run_bot()

            return await func(self, mocker, *args, **kwargs)

        return wrapper_chat

    return decorator_chat


class ChatTestCase:
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    group_internal_id = "Mg8LQTdaZJs8+LJCrtQgblqHx+xI2dX9JJ8hVA2kqt8="
    group_name = "Test"
    group_id = "group.OyZzqio1xDmYiLsQ1VsqRcUFOU4tK2TcECmYt2KeozHJwglMBHAPS7jlkrm="
    config = MappingProxyType(
        {
            "signal_service": signal_service,
            "phone_number": phone_number,
            "storage": {"type": "in-memory"},
        }
    )

    def setup(self) -> None:
        self.signal_bot = SignalBot(ChatTestCase.config)

    async def run_bot(self):  # noqa: ANN201
        producer_id = 1337
        handler_ir = 4444
        await self.signal_bot._produce(producer_id)  # noqa: SLF001
        while self.signal_bot._q.qsize() > 0:  # noqa: SLF001
            await self.signal_bot._consume_new_item(handler_ir)  # noqa: SLF001

    @classmethod
    def new_message(cls, text) -> str:  # noqa: ANN001
        timestamp = time.time()
        new_uuid = str(uuid.uuid4())
        message = {
            "envelope": {
                "source": ChatTestCase.phone_number,
                "sourceNumber": ChatTestCase.phone_number,
                "sourceUuid": new_uuid,
                "sourceName": "some_source_name",
                "sourceDevice": 1,
                "timestamp": timestamp,
                "syncMessage": {
                    "sentMessage": {
                        "timestamp": timestamp,
                        "message": text,
                        "expiresInSeconds": 0,
                        "viewOnce": False,
                        "mentions": [],
                        "attachments": [],
                        "contacts": [],
                        "groupInfo": {
                            "groupId": ChatTestCase.group_internal_id,
                            "type": "DELIVER",
                        },
                        "destination": None,
                        "destinationNumber": None,
                        "destinationUuid": None,
                    },
                },
            },
        }
        return json.dumps(message)


class ReceiveMessagesMock(MagicMock):
    def define(self, messages: list) -> None:
        json_messages = [ChatTestCase.new_message(m) for m in messages]
        mock_iterator = AsyncMock()
        mock_iterator.__aiter__.return_value = json_messages
        self.return_value = mock_iterator


class SendMessagesMock(AsyncMock):
    def __init__(self, **kwargs: str) -> None:
        super().__init__(**kwargs)
        mock = AsyncMock()
        mock.return_value = {"timestamp": "1638715559464"}
        self.return_value = AsyncMock(
            spec=aiohttp.ClientResponse,
            status_code=201,
            json=mock,
        )

    def results(self) -> list:
        return self._extract_responses()

    def _extract_responses(self) -> list:
        return [args[0] for args in self.call_args_list]


class ReactMessageMock(AsyncMock):
    def results(self) -> list:
        return self._extract_responses()

    def _extract_responses(self) -> list:
        return [args[0] for args in self.call_args_list]


class GetGroupsMock(AsyncMock):
    def __init__(self, **kwargs: str) -> None:
        super().__init__(**kwargs)
        self.return_value = [
            {
                "id": ChatTestCase.group_id,
                "internal_id": ChatTestCase.group_internal_id,
                "name": ChatTestCase.group_name,
            }
        ]


class DummyCommand(Command):
    async def handle(self, context: Context) -> None:
        pass
