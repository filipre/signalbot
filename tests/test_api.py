import unittest
from unittest.mock import AsyncMock, patch

import aiohttp

from signalbot import SignalAPI


class TestAPI(unittest.IsolatedAsyncioTestCase):
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    group_id = "group_id1"
    group_secret = "group.group_secret1"  # noqa: S105
    groups = {group_id: group_secret}  # noqa: RUF012

    def setUp(self):  # noqa: ANN201
        self.signal_api = SignalAPI(TestAPI.signal_service, TestAPI.phone_number)

    @patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
    async def test_send(self, mock):  # noqa: ANN001, ANN201
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

        self.assertEqual(resp.status_code, 201)  # noqa: PT009

    @patch("websockets.connect")
    async def test_receive(self, mock):  # noqa: ANN001, ANN201
        message1 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 1","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa: E501
        message2 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 2","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa: E501
        messages = [message1, message2]
        mock_iterator = AsyncMock()
        mock_iterator.__aiter__.return_value = messages
        mock.return_value.__aenter__.return_value = mock_iterator

        results = []
        async for raw_message in self.signal_api.receive():
            results.append(raw_message)  # noqa: PERF401

        self.assertEqual(len(results), 2)  # noqa: PT009
        for i, _ in enumerate(results):
            self.assertEqual(messages[i], results[i])  # noqa: PT009

    def test_receive_uri(self):  # noqa: ANN201
        expected_uri = f"wss://{self.signal_service}/v1/receive/{self.phone_number}"
        actual_uri = self.signal_api._signal_api_uris.receive_ws_uri()  # noqa: SLF001
        self.assertEqual(actual_uri, expected_uri)  # noqa: PT009

    def test_send_uri(self):  # noqa: ANN201
        expected_uri = f"https://{self.signal_service}/v2/send"
        actual_uri = self.signal_api._signal_api_uris.send_rest_uri()  # noqa: SLF001
        self.assertEqual(actual_uri, expected_uri)  # noqa: PT009

    def test_attachment_rest_uri(self):  # noqa: ANN201
        expected_uri = f"https://{self.signal_service}/v1/attachments"
        actual_uri = self.signal_api._signal_api_uris.attachment_rest_uri()  # noqa: SLF001
        self.assertEqual(actual_uri, expected_uri)  # noqa: PT009


if __name__ == "__main__":
    unittest.main()
