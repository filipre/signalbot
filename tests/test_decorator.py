import logging
import unittest
from unittest.mock import patch

from signalbot import Command, Context, enable_console_logging, triggered
from signalbot.command import regex_triggered
from signalbot.utils import ChatTestCase, ReceiveMessagesMock, SendMessagesMock


class TriggeredCommand(Command):
    def describe(self) -> str:
        return "😤 Triggered Command: Decorator Example"

    @triggered("Trump", "Biden")
    async def handle(self, c: Context):  # noqa: ANN201
        await c.send("I am triggered")


class TriggeredCaseSensitiveCommand(Command):
    def describe(self) -> str:
        return "😤 Triggered Command: Decorator Example"

    @triggered("Trump", "Biden", case_sensitive=True)
    async def handle(self, c: Context):  # noqa: ANN201
        await c.send("I am triggered")


class RegexTriggeredCommand(Command):
    def describe(self) -> str:
        return "😤 Triggered Command: Regular Expression Decorator Example"

    @regex_triggered(r"\w+@\w+\.\w+", r"\d{3}-\d{3}-\d{4}")
    async def handle(self, c: Context):  # noqa: ANN201
        await c.send("I am triggered by regular expressions")


class TriggeredTest(ChatTestCase):
    def setUp(self):  # noqa: ANN201
        super().setUp()
        group = {"id": "asdf", "name": "Test"}
        self.signal_bot._groups_by_internal_id = {"group_id1=": group}  # noqa: SLF001
        self.signal_bot.register(TriggeredCommand(), contacts=True, groups=True)

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_triggered(self, receive_mock, send_mock):  # noqa: ANN001, ANN201
        receive_mock.define(["Trump"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 1)  # noqa: PT009

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_also_triggered(self, receive_mock, send_mock):  # noqa: ANN001, ANN201
        receive_mock.define(["Biden"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 1)  # noqa: PT009

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_not_triggered(self, receive_mock, send_mock):  # noqa: ANN001, ANN201
        receive_mock.define(["Scholz"])
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 0)  # noqa: PT009


class TriggeredCaseSensitiveTest(ChatTestCase):
    def setUp(self):  # noqa: ANN201
        super().setUp()
        group = {"id": "asdf", "name": "Test"}
        self.signal_bot._groups_by_internal_id = {"group_id1=": group}  # noqa: SLF001
        self.signal_bot.register(TriggeredCaseSensitiveCommand())

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_triggered(self, receive_mock, send_mock):  # noqa: ANN001, ANN201
        receive_mock.define(["Trump"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 1)  # noqa: PT009

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_not_triggered(self, receive_mock, send_mock):  # noqa: ANN001, ANN201
        receive_mock.define(["trump"])
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 0)  # noqa: PT009


class RegexTriggeredTest(ChatTestCase):
    def setUp(self):  # noqa: ANN201
        super().setUp()
        group = {"id": "asdf", "name": "Test"}
        self.signal_bot._groups_by_internal_id = {"group_id1=": group}  # noqa: SLF001
        self.signal_bot.register(RegexTriggeredCommand())

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_regex_triggered(self, receive_mock, send_mock):  # noqa: ANN001, ANN201
        receive_mock.define(["potus@whitehouse.tld"])
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 1)  # noqa: PT009

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_regex_triggered(self, receive_mock, send_mock):  # noqa: ANN001, ANN201, F811
        receive_mock.define(["123-555-1234"])
        await self.signal_bot._resolve_commands()  # noqa: SLF001
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 1)  # noqa: PT009

    @patch("signalbot.SignalAPI.send", new_callable=SendMessagesMock)
    @patch("signalbot.SignalAPI.receive", new_callable=ReceiveMessagesMock)
    async def test_not_regex_triggered(self, receive_mock, send_mock):  # noqa: ANN001, ANN201
        receive_mock.define(["11-222"])
        await self.run_bot()
        self.assertEqual(send_mock.call_count, 0)  # noqa: PT009


if __name__ == "__main__":
    enable_console_logging(logging.INFO)
    unittest.main()
