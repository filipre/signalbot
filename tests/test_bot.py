import asyncio

import aiohttp
import pytest
from pytest_mock import MockerFixture

from signalbot import Command, SignalAPI, SignalBot
from signalbot.context import Context
from signalbot.utils import DummyCommand


class TestCommon:
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"
    group_id = "group.group_secret1="
    internal_id = "group_id1="

    @pytest.fixture(autouse=True)
    def setup(self):
        config = {
            "signal_service": self.signal_service,
            "phone_number": self.phone_number,
            "storage": {"type": "in-memory"},
        }
        self.signal_bot = SignalBot(config)


class TestProducer(TestCommon):
    @pytest.mark.asyncio
    async def test_produce(self, mocker: MockerFixture):
        # Two messages
        message1 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 1","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group_id1=","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa: E501
        message2 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 2","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group_id1=","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa: E501
        messages = [message1, message2]
        mock_iterator = mocker.AsyncMock()
        mock_iterator.__aiter__.return_value = messages
        mock = mocker.patch("websockets.connect")
        mock.return_value.__aenter__.return_value = mock_iterator

        group_mock = mocker.AsyncMock()
        group_mock.return_value = [
            {
                "name": "mocked group",
                "id": self.group_id,
                "internal_id": self.internal_id,
            },
        ]
        get_group_mock = mocker.patch(
            "aiohttp.ClientSession.get", new_callable=mocker.AsyncMock
        )
        get_group_mock.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status_code=200,
            json=group_mock,
        )

        self.signal_bot._q = asyncio.Queue()  # noqa: SLF001
        self.signal_bot._signal = SignalAPI(  # noqa: SLF001
            self.signal_service,
            self.phone_number,
        )

        # Any two commands
        self.signal_bot.register(DummyCommand())
        self.signal_bot.register(DummyCommand())
        await self.signal_bot._resolve_commands()  # noqa: SLF001

        await self.signal_bot._produce(1337)  # noqa: SLF001

        assert self.signal_bot._q.qsize() == 4  # noqa: PLR2004, SLF001


class TestUsernameValidation(TestCommon):
    def test_valid_username(self):
        valid_usernames = [
            "Usr.99",
            "UserName.99",
            "username.999999999",
            "UserName99.99",
            "_Use_rName99_.99",
            "usernameeeeeeeeeeeeeeeeeeeeeeeee.999999999",
        ]
        for valid_username in valid_usernames:
            assert self.signal_bot._is_username(valid_username)  # noqa: SLF001

    def test_invalid_username(self):
        invalid_usernames = [
            "Us.99",
            "Usr.9",
            ".UserName99",
            ".UserName.99",
            "UserName99",
            "UserName99.",
            "username.9999999999",
            "user@name.999",
            "UserName99.0",
            "UserName99.00",
            "UserName99.000000000",
            ".usernameeeeeeeeeeeeeeeeeeeeeeeeee.99",
        ]
        for invalid_username in invalid_usernames:
            assert not self.signal_bot._is_username(invalid_username)  # noqa: SLF001


class TestRegisterCommand(TestCommon):
    def test_register_one_command(self):
        self.signal_bot.register(DummyCommand())
        assert len(self.signal_bot._commands_to_be_registered) == 1  # noqa: SLF001

    def test_register_three_commands(self):
        self.signal_bot.register(DummyCommand())
        self.signal_bot.register(DummyCommand())
        self.signal_bot.register(DummyCommand())
        assert len(self.signal_bot._commands_to_be_registered) == 3  # noqa: PLR2004, SLF001

    def test_register_calls_setup_of_command(self):
        class SomeTestCommand(Command):
            def __init__(self):  # noqa: ANN204
                self.state = False

            def setup(self):  # noqa: ANN202
                self.state = True

            def handle(self, context: Context):  # noqa: ANN202
                pass

        cmd = SomeTestCommand()
        assert cmd.state is False

        self.signal_bot.register(cmd)
        assert cmd.state is True

    @pytest.mark.asyncio
    async def test_register_single_contact(self):
        user_number = "+49987654321"
        self.signal_bot.register(DummyCommand(), contacts=[user_number])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        assert self.signal_bot.commands[0][1] == [user_number]

    @pytest.mark.asyncio
    async def test_register_multiple_contacts(self):
        user_number1 = "+49987654321"
        user_number2 = "+49987654322"
        user_number3 = "+49987654323"
        self.signal_bot.register(
            DummyCommand(),
            contacts=[user_number1, user_number2, user_number3],
        )
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        expected_user_chats = [user_number1, user_number2, user_number3]
        assert self.signal_bot.commands[0][1] == expected_user_chats

    @pytest.mark.asyncio
    async def test_register_multiple_contacts_multiple_commands(self):
        user_number1 = "+49987654321"
        user_number2 = "+49987654322"
        user_number3 = "+49987654323"
        self.signal_bot.register(DummyCommand(), contacts=[user_number1, user_number2])
        self.signal_bot.register(DummyCommand(), contacts=[user_number3])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        expected_user_chats_cmd0 = [user_number1, user_number2]
        expected_user_chats_cmd1 = [user_number3]
        assert self.signal_bot.commands[0][1] == expected_user_chats_cmd0
        assert self.signal_bot.commands[1][1] == expected_user_chats_cmd1
