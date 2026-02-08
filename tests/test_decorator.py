from dataclasses import dataclass

import pytest
from pytest_mock import MockerFixture

from signalbot import Command, Context, triggered
from signalbot.command import regex_triggered
from signalbot.utils import (
    ChatTestCase,
    GetGroupsMock,
    ReceiveMessagesMock,
    SendMessagesMock,
)


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


@dataclass
class SendReceiveGetGroupsMocks:
    send_mock: SendMessagesMock
    receive_mock: ReceiveMessagesMock
    get_groups_mock: GetGroupsMock


@pytest.mark.asyncio
class TestCommon(ChatTestCase):
    def mock_send_receive_get_groups(
        self, mocker: MockerFixture
    ) -> SendReceiveGetGroupsMocks:
        send_mock = mocker.patch(
            "signalbot.SignalAPI.send", new_callable=SendMessagesMock
        )
        receive_mock = mocker.patch(
            "signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock
        )
        get_groups_mock = mocker.patch(
            "signalbot.SignalAPI.get_groups",
            new_callable=GetGroupsMock,
        )
        return SendReceiveGetGroupsMocks(send_mock, receive_mock, get_groups_mock)


class TestTriggered(TestCommon):
    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()
        self.signal_bot.register(TriggeredCommand(), contacts=True, groups=True)

    async def test_triggered(self, mocker: MockerFixture):
        mocks = self.mock_send_receive_get_groups(mocker)
        mocks.receive_mock.define(["Trump"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert mocks.send_mock.call_count == 1

    async def test_also_triggered(self, mocker: MockerFixture):
        mocks = self.mock_send_receive_get_groups(mocker)
        mocks.receive_mock.define(["Biden"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert mocks.send_mock.call_count == 1

    async def test_not_triggered(self, mocker: MockerFixture):
        mocks = self.mock_send_receive_get_groups(mocker)
        mocks.receive_mock.define(["Scholz"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert mocks.send_mock.call_count == 0


class TestTriggeredCaseSensitive(TestCommon):
    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()
        self.signal_bot.register(TriggeredCaseSensitiveCommand())

    async def test_triggered(self, mocker: MockerFixture):
        mocks = self.mock_send_receive_get_groups(mocker)
        mocks.receive_mock.define(["Trump"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert mocks.send_mock.call_count == 1

    async def test_not_triggered(self, mocker: MockerFixture):
        mocks = self.mock_send_receive_get_groups(mocker)
        mocks.receive_mock.define(["trump"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert mocks.send_mock.call_count == 0


class TestRegexTriggered(TestCommon):
    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()
        self.signal_bot.register(RegexTriggeredCommand())

    async def test_regex_triggered_email(self, mocker: MockerFixture):
        mocks = self.mock_send_receive_get_groups(mocker)
        mocks.receive_mock.define(["potus@whitehouse.tld"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert mocks.send_mock.call_count == 1

    async def test_regex_triggered_phone(self, mocker: MockerFixture):
        mocks = self.mock_send_receive_get_groups(mocker)
        mocks.receive_mock.define(["123-555-1234"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert mocks.send_mock.call_count == 1

    async def test_not_regex_triggered(self, mocker: MockerFixture):
        mocks = self.mock_send_receive_get_groups(mocker)
        mocks.receive_mock.define(["11-222"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert mocks.send_mock.call_count == 0


class TestTriggeredGroups(TestCommon):
    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()

    async def _test_trigger(self, mocker: MockerFixture, call_count: int) -> None:
        mocks = self.mock_send_receive_get_groups(mocker)
        mocks.receive_mock.define(["Trump"])
        await self.signal_bot._detect_groups()  # noqa: SLF001
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert mocks.send_mock.call_count == call_count

    async def test_triggered_name(self, mocker: MockerFixture):
        self.signal_bot.register(TriggeredCommand(), groups=[ChatTestCase.group_name])
        await self._test_trigger(mocker, call_count=1)

    async def test_triggered_id(self, mocker: MockerFixture):
        self.signal_bot.register(TriggeredCommand(), groups=[ChatTestCase.group_id])
        await self._test_trigger(mocker, call_count=1)

    async def test_triggered_internal_id(self, mocker: MockerFixture):
        self.signal_bot.register(
            TriggeredCommand(), groups=[ChatTestCase.group_internal_id]
        )
        await self._test_trigger(mocker, call_count=1)

    async def test_not_triggered_name(self, mocker: MockerFixture):
        self.signal_bot.register(
            TriggeredCommand(), groups=[ChatTestCase.group_name + "a"]
        )
        await self._test_trigger(mocker, call_count=0)

    async def test_not_triggered_id(self, mocker: MockerFixture):
        self.signal_bot.register(
            TriggeredCommand(), groups=[ChatTestCase.group_id + "a"]
        )
        await self._test_trigger(mocker, call_count=0)

    async def test_not_triggered_internal_id(self, mocker: MockerFixture):
        self.signal_bot.register(
            TriggeredCommand(), groups=[ChatTestCase.group_internal_id + "a"]
        )
        await self._test_trigger(mocker, call_count=0)
