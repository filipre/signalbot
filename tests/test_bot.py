import unittest
import asyncio
from unittest.mock import patch, AsyncMock
from signalbot import SignalBot, Command, SignalAPI


class BotTestCase(unittest.IsolatedAsyncioTestCase):
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"
    group_id = "group.group_secret1="
    internal_id = "group_id1="

    def setUp(self):
        config = {
            "signal_service": BotTestCase.signal_service,
            "phone_number": BotTestCase.phone_number,
        }
        self.signal_bot = SignalBot(config)


class TestProducer(BotTestCase):
    @patch("websockets.connect")
    async def test_produce(self, mock):
        # Two messages
        message1 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 1","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group_id1=","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa
        message2 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 2","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group_id1=","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa
        messages = [message1, message2]
        mock_iterator = AsyncMock()
        mock_iterator.__aiter__.return_value = messages
        mock.return_value.__aenter__.return_value = mock_iterator

        self.signal_bot._q = asyncio.Queue()
        self.signal_bot._signal = SignalAPI(
            TestProducer.signal_service, TestProducer.phone_number
        )
        self.signal_bot.listen(TestProducer.group_id, TestProducer.internal_id)
        # Any two commands
        self.signal_bot.register(Command())
        self.signal_bot.register(Command())

        await self.signal_bot._produce(1337)

        self.assertEqual(self.signal_bot._q.qsize(), 4)


class TestListenUser(BotTestCase):
    def test_listen_phone_number(self):
        user_number = "+49987654321"
        self.signal_bot.listen(user_number)
        expected_user_chats = {user_number}
        self.assertSetEqual(self.signal_bot.user_chats, expected_user_chats)

    def test_listenUser_phone_number(self):
        user_number = "+49987654321"
        self.signal_bot.listenUser(user_number)
        expected_user_chats = {user_number}
        self.assertSetEqual(self.signal_bot.user_chats, expected_user_chats)

    def test_listen_multiple_user_chats(self):
        user_number1 = "+49987654321"
        user_number2 = "+49987654322"
        user_number3 = "+49987654323"
        self.signal_bot.listen(user_number1)
        self.signal_bot.listen(user_number2)
        self.signal_bot.listen(user_number3)
        expected_user_chats = {user_number1, user_number3, user_number2}
        self.assertSetEqual(self.signal_bot.user_chats, expected_user_chats)

    def test_listenUser_multiple_user_chats(self):
        user_number1 = "+49987654321"
        user_number2 = "+49987654322"
        user_number3 = "+49987654323"
        self.signal_bot.listenUser(user_number1)
        self.signal_bot.listenUser(user_number2)
        self.signal_bot.listenUser(user_number3)
        expected_user_chats = {user_number1, user_number3, user_number2}
        self.assertSetEqual(self.signal_bot.user_chats, expected_user_chats)

    def test_listen_invalid_phone_number(self):
        invalid_number = "49987654321"
        self.signal_bot.listen(invalid_number)
        expected_user_chats = set()
        self.assertSetEqual(self.signal_bot.user_chats, expected_user_chats)

    def test_listenUser_invalid_phone_number(self):
        invalid_number = "49987654321"
        self.signal_bot.listenUser(invalid_number)
        expected_user_chats = set()
        self.assertSetEqual(self.signal_bot.user_chats, expected_user_chats)

    def test_listen_valid_invalid_phone_number(self):
        invalid_number = "49987654321"
        valid_number = "+49123454321"
        self.signal_bot.listen(invalid_number)
        self.signal_bot.listen(valid_number)
        expected_user_chats = {valid_number}
        self.assertSetEqual(self.signal_bot.user_chats, expected_user_chats)


class TestRegisterCommand(BotTestCase):
    def test_register_one_command(self):
        self.signal_bot.register(Command())
        self.assertEqual(len(self.signal_bot.commands), 1)

    def test_register_three_commands(self):
        self.signal_bot.register(Command())
        self.signal_bot.register(Command())
        self.signal_bot.register(Command())
        self.assertEqual(len(self.signal_bot.commands), 3)

    def test_register_calls_setup_of_command(self):
        class SomeTestCommand(Command):
            def __init__(self):
                self.state = False

            def setup(self):
                self.state = True

        cmd = SomeTestCommand()
        self.assertEqual(cmd.state, False)

        self.signal_bot.register(cmd)
        self.assertEqual(cmd.state, True)
