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


@pytest.mark.asyncio
class TestCommon(ChatTestCase):
    def setup(self):
        super().setup()
        group = {"id": ChatTestCase.group_id, "name": ChatTestCase.group_name}
        self.signal_bot._groups_by_internal_id = {ChatTestCase.group_internal_id: group}  # noqa: SLF001
        self.signal_bot._groups_by_id = {ChatTestCase.group_id: group}  # noqa: SLF001
        self.signal_bot._groups_by_name = {ChatTestCase.group_name: [group]}  # noqa: SLF001

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

    async def test_triggered(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["Trump"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert send_mock.call_count == 1

    async def test_also_triggered(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["Biden"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert send_mock.call_count == 1

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

    async def test_triggered(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["Trump"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert send_mock.call_count == 1

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

    async def test_regex_triggered_email(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["potus@whitehouse.tld"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert send_mock.call_count == 1

    async def test_regex_triggered_phone(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["123-555-1234"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert send_mock.call_count == 1

    async def test_not_regex_triggered(self, mocker: MockerFixture):
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["11-222"])
        await self.run_bot()
        assert send_mock.call_count == 0


class TestTriggeredGroups(TestCommon):
    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()

    async def _test_trigger(self, mocker: MockerFixture, call_count: int) -> None:
        send_mock, receive_mock = self.mock_send_receive(mocker)
        receive_mock.define(["Trump"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        assert send_mock.call_count == call_count

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
