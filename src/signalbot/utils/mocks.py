import time
import aiohttp
from unittest.mock import AsyncMock, MagicMock
from .chat import ChatTestCase


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

    def results(self):
        results = []
        for args in self.call_args_list:
            results.append(args[0])
        return results


class ReactMessageMock(AsyncMock):
    def results(self):
        results = []
        for args in self.call_args_list:
            results.append(args[0])
        return results
