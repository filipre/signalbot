import functools
import json
import time
import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp

from signalbot.bot import Command, Context, SignalBot


def chat(*messages):  # noqa: ANN002, ANN201
    def decorator_chat(func):  # noqa: ANN001, ANN202
        signalbot_package = ".".join(__package__.split(".")[:-1])

        @functools.wraps(func)
        @patch(f"{signalbot_package}.SignalAPI.react", new_callable=ReactMessageMock)
        @patch(f"{signalbot_package}.SignalAPI.send", new_callable=SendMessagesMock)
        @patch(
            f"{signalbot_package}.SignalAPI.receive",
            new_callable=ReceiveMessagesMock,
        )
        async def wrapper_chat(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            chat_test_case = args[0]
            receive_mock = args[1]

            receive_mock.define(messages)
            await chat_test_case.run_bot()

            value = func(*args, **kwargs)
            return value  # noqa: RET504

        return wrapper_chat

    return decorator_chat


class ChatTestCase(unittest.IsolatedAsyncioTestCase):
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    group_id = "group_id1="
    group_secret = "group.group_secret1="  # noqa: S105
    config = {  # noqa: RUF012
        "signal_service": signal_service,
        "phone_number": phone_number,
        "storage": {"type": "in-memory"},
    }

    def setUp(self):  # noqa: ANN201
        self.signal_bot = SignalBot(ChatTestCase.config)

    async def run_bot(self):  # noqa: ANN201
        PRODUCER_ID = 1337  # noqa: N806
        HANDLER_ID = 4444  # noqa: N806
        await self.signal_bot._produce(PRODUCER_ID)  # noqa: SLF001
        while self.signal_bot._q.qsize() > 0:  # noqa: SLF001
            await self.signal_bot._consume_new_item(HANDLER_ID)  # noqa: SLF001

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
                            "groupId": ChatTestCase.group_id,
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
    def define(self, messages: list):  # noqa: ANN201
        json_messages = [ChatTestCase.new_message(m) for m in messages]
        mock_iterator = AsyncMock()
        mock_iterator.__aiter__.return_value = json_messages
        self.return_value = mock_iterator


class SendMessagesMock(AsyncMock):
    def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003, ANN204
        super().__init__(*args, **kwargs)
        mock = AsyncMock()
        mock.return_value = {"timestamp": "1638715559464"}
        self.return_value = AsyncMock(
            spec=aiohttp.ClientResponse,
            status_code=201,
            json=mock,
        )

    def results(self) -> list:
        return self._extract_responses()

    def _extract_responses(self):  # noqa: ANN202
        results = []
        for args in self.call_args_list:
            results.append(args[0])  # noqa: PERF401
        return results


class ReactMessageMock(AsyncMock):
    def results(self) -> list:
        return self._extract_responses()

    def _extract_responses(self):  # noqa: ANN202
        results = []
        for args in self.call_args_list:
            results.append(args[0])  # noqa: PERF401
        return results


class DummyCommand(Command):
    async def handle(self, context: Context):  # noqa: ANN201
        pass
