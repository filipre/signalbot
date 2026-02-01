import aiohttp
import pytest
from pytest_mock import MockerFixture

from signalbot import SignalAPI


class TestAPI:
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    group_id = "group_id1"
    group_secret = "group.group_secret1"  # noqa: S105
    groups = {group_id: group_secret}  # noqa: RUF012

    @pytest.fixture(autouse=True)
    def setup(self):
        self.signal_api = SignalAPI(self.signal_service, self.phone_number)

    @pytest.mark.asyncio
    async def test_send(self, mocker: MockerFixture):
        status_code = 201
        mock2 = mocker.AsyncMock()
        mock2.return_value = {"timestamp": "1638715559464"}

        mock = mocker.patch("aiohttp.ClientSession.post", new_callable=mocker.AsyncMock)
        mock.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status_code=status_code,
            json=mock2,
        )

        receiver = self.group_id
        message = "Hello World!"
        resp = await self.signal_api.send(receiver, message)

        assert resp.status_code == status_code

    @pytest.mark.asyncio
    async def test_receive(self, mocker: MockerFixture):
        message1 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 1","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa: E501
        message2 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 2","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa: E501
        messages = [message1, message2]
        mock_iterator = mocker.AsyncMock()
        mock_iterator.__aiter__.return_value = messages
        mock = mocker.patch("websockets.connect")
        mock.return_value.__aenter__.return_value = mock_iterator

        results = [raw_message async for raw_message in self.signal_api.receive()]

        assert len(results) == len(messages)
        for i, _ in enumerate(results):
            assert messages[i] == results[i]

    def test_receive_uri(self):
        expected_uri = f"wss://{self.signal_service}/v1/receive/{self.phone_number}"
        actual_uri = self.signal_api._signal_api_uris.receive_ws_uri()  # noqa: SLF001
        assert actual_uri == expected_uri

    def test_send_uri(self):
        expected_uri = f"https://{self.signal_service}/v2/send"
        actual_uri = self.signal_api._signal_api_uris.send_rest_uri()  # noqa: SLF001
        assert actual_uri == expected_uri

    def test_attachment_rest_uri(self):
        expected_uri = f"https://{self.signal_service}/v1/attachments"
        actual_uri = self.signal_api._signal_api_uris.attachment_rest_uri()  # noqa: SLF001
        assert actual_uri == expected_uri
