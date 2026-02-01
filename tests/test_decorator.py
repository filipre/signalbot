import pytest
from pytest_mock import MockerFixture

from signalbot import Command, Context, triggered
from signalbot.command import regex_triggered
from signalbot.utils import ChatTestCase, ReceiveMessagesMock, SendMessagesMock


class TriggeredCommand(Command):
    @triggered("Trump", "Biden")
    async def handle(self, c: Context):
        await c.send("I am triggered")


class TriggeredCaseSensitiveCommand(Command):
    @triggered("Trump", "Biden", case_sensitive=True)
    async def handle(self, c: Context):
        await c.send("I am triggered")


class RegexTriggeredCommand(Command):
    @regex_triggered(r"\w+@\w+\.\w+", r"\d{3}-\d{3}-\d{4}")
    async def handle(self, c: Context):
        await c.send("I am triggered by regular expressions")


class TestCommon(ChatTestCase):
    def setup(self):
        super().setup()
        group = {"id": "asdf", "name": "Test"}
        self.signal_bot._groups_by_internal_id = {"group_id1=": group}  # noqa: SLF001

    def mock_send_receive(
        self, mocker: MockerFixture
    ) -> tuple[SendMessagesMock, ReceiveMessagesMock]:
        send_mock = mocker.patch(
            "signalbot.SignalAPI.send", new_callable=SendMessagesMock
        )
        receive_mock = mocker.patch(
            "signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock
        )
        return send_mock, receive_mock


class TestTriggered(TestCommon):
    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()
        self.signal_bot.register(TriggeredCommand(), contacts=True, groups=True)

    @pytest.mark.asyncio
    async def test_triggered(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["Trump"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert send_mock.call_count == 1

    @pytest.mark.asyncio
    async def test_also_triggered(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["Biden"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert send_mock.call_count == 1

    @pytest.mark.asyncio
    async def test_not_triggered(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["Scholz"])
        await self.run_bot()
        assert send_mock.call_count == 0


class TestTriggeredCaseSensitive(TestCommon):
    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()
        self.signal_bot.register(TriggeredCaseSensitiveCommand())

    @pytest.mark.asyncio
    async def test_triggered(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["Trump"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert send_mock.call_count == 1

    @pytest.mark.asyncio
    async def test_not_triggered(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["trump"])
        await self.run_bot()
        assert send_mock.call_count == 0


class TestRegexTriggered(TestCommon):
    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()
        self.signal_bot.register(RegexTriggeredCommand())

    @pytest.mark.asyncio
    async def test_regex_triggered_email(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["potus@whitehouse.tld"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert send_mock.call_count == 1

    @pytest.mark.asyncio
    async def test_regex_triggered_phone(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["123-555-1234"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert send_mock.call_count == 1

    @pytest.mark.asyncio
    async def test_not_regex_triggered(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["11-222"])
        await self.run_bot()
        assert send_mock.call_count == 0
