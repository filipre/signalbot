import unittest
import aiohttp
from unittest.mock import patch, AsyncMock

from signalbot import SignalAPI


class TestAPI(unittest.IsolatedAsyncioTestCase):
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    group_id = "group_id1"
    group_secret = "group.group_secret1"
    groups = {group_id: group_secret}

    def setUp(self):
        self.signal_api = SignalAPI(TestAPI.signal_service, TestAPI.phone_number)

    @patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
    async def test_send(self, mock):
        mock2 = AsyncMock()
        mock2.return_value = {"timestamp": "1638715559464"}
        mock.return_value = AsyncMock(
            spec=aiohttp.ClientResponse,
            status_code=201,
            json=mock2,
        )

        receiver = TestAPI.group_id
        message = "Hello World!"
        resp = await self.signal_api.send(receiver, message)

        self.assertEqual(resp.status_code, 201)

    @patch("websockets.connect")
    async def test_receive(self, mock):
        message1 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 1","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa
        message2 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 2","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa
        messages = [message1, message2]
        mock_iterator = AsyncMock()
        mock_iterator.__aiter__.return_value = messages
        mock.return_value.__aenter__.return_value = mock_iterator

        results = []
        async for raw_message in self.signal_api.receive():
            results.append(raw_message)

        self.assertEqual(len(results), 2)
        for i, _ in enumerate(results):
            self.assertEqual(messages[i], results[i])

    def test_receive_uri(self):
        expected_uri = f"ws://{self.signal_service}/v1/receive/{self.phone_number}"
        actual_uri = self.signal_api._receive_ws_uri()
        self.assertEqual(actual_uri, expected_uri)

    def test_send_uri(self):
        expected_uri = f"http://{self.signal_service}/v2/send"
        actual_uri = self.signal_api._send_rest_uri()
        self.assertEqual(actual_uri, expected_uri)


if __name__ == "__main__":
    unittest.main()
