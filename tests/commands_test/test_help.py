import unittest

from commands import HelpCommand
from signal_bot import Message, MessageType


class TestHelpCommand(unittest.TestCase):
    def _new_message(self, text: str):
        return Message("source", 123456789, MessageType.DATA_MESSAGE, text)

    def test_trigger_help_word1(self):
        message = self._new_message("help")
        triggered = HelpCommand.triggered(message, HelpCommand.triggers)
        self.assertEqual(triggered, True)

    def test_trigger_help_emoji1(self):
        message = self._new_message("🤖")
        triggered = HelpCommand.triggered(message, HelpCommand.triggers)
        self.assertEqual(triggered, True)


if __name__ == "__main__":
    unittest.main()
