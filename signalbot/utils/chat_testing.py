import unittest
import uuid
import time
import json
import functools
import aiohttp
from unittest.mock import AsyncMock, MagicMock

from ..bot import SignalBot

from unittest.mock import patch


def chat(*messages):
    def decorator_chat(func):
        signalbot_package = ".".join(__package__.split(".")[:-1])

        @functools.wraps(func)
        @patch(f"{signalbot_package}.SignalAPI.react", new_callable=ReactMessageMock)
        @patch(f"{signalbot_package}.SignalAPI.send", new_callable=SendMessagesMock)
        @patch(
            f"{signalbot_package}.SignalAPI.receive", new_callable=ReceiveMessagesMock
        )
        async def wrapper_chat(*args, **kwargs):
            chat_test_case = args[0]
            receive_mock = args[1]

            receive_mock.define(messages)
            await chat_test_case.run_bot()

            value = func(*args, **kwargs)
            return value

        return wrapper_chat

    return decorator_chat


class ChatTestCase(unittest.IsolatedAsyncioTestCase):
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    group_id = "group_id1="
    group_secret = "group.group_secret1="
    config = {
        "signal_service": signal_service,
        "phone_number": phone_number,
    }

    def setUp(self):
        self.signal_bot = SignalBot(ChatTestCase.config)
        self.signal_bot.listen(ChatTestCase.group_id, ChatTestCase.group_secret)

    async def run_bot(self):
        PRODUCER_ID = 1337
        HANDLER_ID = 4444
        await self.signal_bot._produce(PRODUCER_ID)
        while self.signal_bot._q.qsize() > 0:
            await self.signal_bot._consume_new_item(HANDLER_ID)

    @classmethod
    def new_message(cls, text) -> str:
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
                    }
                },
            }
        }
        return json.dumps(message)


class ReceiveMessagesMock(MagicMock):
    def define(self, messages: list):
        json_messages = [ChatTestCase.new_message(m) for m in messages]
        mock_iterator = AsyncMock()
        mock_iterator.__aiter__.return_value = json_messages
        self.return_value = mock_iterator


class SendMessagesMock(AsyncMock):
    def __init__(self, *args, **kwargs):
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

    def _extract_responses(self):
        results = []
        for args in self.call_args_list:
            results.append(args[0])
        return results


class ReactMessageMock(AsyncMock):
    def results(self) -> list:
        return self._extract_responses()

    def _extract_responses(self):
        results = []
        for args in self.call_args_list:
            results.append(args[0])
        return results
