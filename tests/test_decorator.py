import unittest
from unittest.mock import patch
import logging
from signalbot import Command, Context, triggered
from signalbot.utils import ChatTestCase, SendMessagesMock, ReceiveMessagesMock


class TriggeredCommand(Command):
    def describe(self) -> str:
        return "😤 Triggered Command: Decorator Example"

    @triggered("Trump", "Biden")
    async def handle(self, c: Context):
        await c.send("I am triggered")


class TriggeredCaseSensitiveCommand(Command):
    def describe(self) -> str:
        return "😤 Triggered Command: Decorator Example"

    @triggered("Trump", "Biden", case_sensitive=True)
    async def handle(self, c: Context):
        await c.send("I am triggered")


class TriggeredTest(ChatTestCase):
    def setUp(self):
        super().setUp()
        group = {"id": "asdf", "name": "Test"}
        self.signal_bot._groups_by_internal_id = {"group_id1=": group}
        self.signal_bot.register(TriggeredCommand(), contacts=True, groups=True)

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_triggered(self, receive_mock, send_mock):
        receive_mock.define(["Trump"])
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 1)

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_also_triggered(self, receive_mock, send_mock):
        receive_mock.define(["Biden"])
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 1)

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_not_triggered(self, receive_mock, send_mock):
        receive_mock.define(["Scholz"])
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 0)


class TriggeredCaseSensitiveTest(ChatTestCase):
    def setUp(self):
        super().setUp()
        group = {"id": "asdf", "name": "Test"}
        self.signal_bot._groups_by_internal_id = {"group_id1=": group}
        self.signal_bot.register(TriggeredCaseSensitiveCommand())

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_triggered(self, receive_mock, send_mock):
        receive_mock.define(["Trump"])
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 1)

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_not_triggered(self, receive_mock, send_mock):
        receive_mock.define(["trump"])
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 0)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    unittest.main()
