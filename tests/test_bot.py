import unittest
import asyncio
from unittest.mock import patch, AsyncMock
from src.signalbot import SignalBot, Command, SignalAPI


class TestBot(unittest.IsolatedAsyncioTestCase):
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    group_id = "group_id1"
    group_secret = "group.group_secret1"
    config = {"groups": {group_id: group_secret}}

    def setUp(self):
        config = {
            "signal_service": TestBot.signal_service,
            "phone_number": TestBot.phone_number,
        }
        self.signal_bot = SignalBot(config)

    @patch("websockets.connect")
    async def test_produce(self, mock):
        # Two messages
        message1 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 1","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group_id1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa
        message2 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 2","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group_id1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa
        messages = [message1, message2]
        mock_iterator = AsyncMock()
        mock_iterator.__aiter__.return_value = messages
        mock.return_value.__aenter__.return_value = mock_iterator

        self.signal_bot._q = asyncio.Queue()
        self.signal_bot._signal = SignalAPI(
            TestBot.signal_service, TestBot.phone_number
        )
        self.signal_bot.listen(TestBot.group_id, TestBot.group_secret)
        # Any two commands
        self.signal_bot.register(Command())
        self.signal_bot.register(Command())

        await self.signal_bot._produce(1337)

        self.assertEqual(self.signal_bot._q.qsize(), 4)
