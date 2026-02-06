import pytest
from pytest_mock import MockerFixture

from signalbot.utils import ChatTestCase, chat

from ..ping import PingCommand  # noqa: TID252


class TestPingChatTest(ChatTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()
        self.signal_bot.register(PingCommand())

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings(
        "ignore:There is no current event loop:DeprecationWarning"
    )
    @chat("ping")
    async def test_ping(self, mocker: MockerFixture, *args: object, **kwargs: object):  # noqa: ARG002
        replies = self.signal_bot._signal.send  # noqa: SLF001
        assert replies.call_count == 1
        assert len(replies.results()) == 1
        for recipient, message in replies.results():
            assert recipient == ChatTestCase.group_secret
            assert message == "pong"
