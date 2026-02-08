import pytest
from pytest_mock import MockerFixture

from signalbot import Command, Context, triggered
from signalbot.utils import ChatTestCase, mock_chat


class SchnickSchnackSchnuckCommand(Command):
    @triggered("schnick", "schnack")
    async def handle(self, c: Context) -> bool:
        text = c.message.text
        if text == "schnick":
            await c.send("schnack")

        if text == "schnack":
            await c.send("schnuck")


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore:There is no current event loop:DeprecationWarning")
class TestSchnickSchnackSchnuckCommand(ChatTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()
        self.signal_bot.register(SchnickSchnackSchnuckCommand())

    @mock_chat("schnick")
    async def test_schnick(
        self,
        mocker: MockerFixture,  # noqa: ARG002
        *args: object,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ):
        replies = self.signal_bot._signal.send  # noqa: SLF001
        assert replies.call_count == 1
        assert len(replies.results()) == 1
        for recipient, message in replies.results():
            assert recipient == ChatTestCase.group_id
            assert message == "schnack"

    @mock_chat("schnack")
    async def test_schnack(
        self,
        mocker: MockerFixture,  # noqa: ARG002
        *args: object,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ):
        replies = self.signal_bot._signal.send  # noqa: SLF001
        assert replies.call_count == 1
        assert len(replies.results()) == 1
        for recipient, message in replies.results():
            assert recipient == ChatTestCase.group_id
            assert message == "schnuck"
