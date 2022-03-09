import unittest
from signalbot.utils import ChatTestCase, chat
from commands.ping import PingCommand


class PingChatTest(ChatTestCase):
    def setUp(self):
        super().setUp()
        self.signal_bot.register(PingCommand())

    @chat("ping")
    async def test_ping(self, query, replies, reactions):
        self.assertEqual(replies.call_count, 1)
        for recipient, message in replies.results():
            self.assertEqual(recipient, ChatTestCase.group_secret)
            self.assertEqual(message, "pong")


if __name__ == "__main__":
    unittest.main()
