import unittest

from signalbot.utils import ChatTestCase, chat

from ..ping import PingCommand  # noqa: TID252


class PingChatTest(ChatTestCase):
    def setUp(self):  # noqa: ANN201
        super().setUp()
        self.signal_bot.register(PingCommand())

    @chat("ping")
    async def test_ping(self, query, replies, reactions):  # noqa: ANN001, ANN201, ARG002
        self.assertEqual(replies.call_count, 1)  # noqa: PT009
        for recipient, message in replies.results():
            self.assertEqual(recipient, ChatTestCase.group_secret)  # noqa: PT009
            self.assertEqual(message, "pong")  # noqa: PT009


if __name__ == "__main__":
    unittest.main()
