import unittest
from unittest.mock import patch
import asyncio
import logging
from signalbot import Command, Context
from signalbot.utils import (
    ChatTestCase,
    SendMessagesMock,
    ReceiveMessagesMock,
    chat,
)


class ChingChangChongCommand(Command):
    triggers = ["ching", "chang"]

    def __init__(self, listen):
        self.listen = listen

    async def handle(self, c: Context) -> bool:
        if not Command.triggered(c.message, self.triggers):
            return

        text = c.message.text
        if text == "ching":
            await asyncio.sleep(1)
            await c.send("chang", listen=self.listen)
            return

        if text == "chang":
            await asyncio.sleep(1)
            await c.send("chong")
            return


# class EnabledListenChatTest(ChatTestCase):
#     def setUp(self):
#         super().setUp()
#         self.signal_bot.register(ChingChangChongCommand(listen=True))

#     @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
#     @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
#     async def test_chat(self, receive_mock, send_mock):
#         receive_mock.define(["ching"])
#         await self.run_bot()
#         self.assertEqual(send_mock.call_count, 2)


# class DisabledListenChatTest(ChatTestCase):
#     def setUp(self):
#         super().setUp()
#         group = {"id": "asdf", "name": "Test"}
#         self.signal_bot._groups_by_internal_id = {"group_id1=": group}
#         self.signal_bot.register(ChingChangChongCommand(listen=False))

#     @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
#     @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
#     async def test_chat(self, receive_mock, send_mock):
#         receive_mock.define(["ching"])
#         await self.run_bot()
#         self.assertEqual(send_mock.call_count, 1)


# class DecoratorChatTest(ChatTestCase):
#     def setUp(self):
#         super().setUp()
#         self.signal_bot.register(ChingChangChongCommand(listen=True))

#     @chat("how are you doing", "ching")
#     def test_chat(self, query, replies, reactions):
#         self.assertEqual(replies.call_count, 2)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    unittest.main()
