import unittest

from commands import TimeCommand
from signal_bot import Message, MessageType


class TestTimeCommand(unittest.TestCase):
    def _new_message(self, text: str):
        return Message("source", 123456789, MessageType.DATA_MESSAGE, text)

    def test_trigger_uhrzeit_emoji(self):
        message = self._new_message("🕰")
        triggered = TimeCommand.triggered(message, TimeCommand.triggers)
        self.assertEqual(triggered, True)

    def test_trigger_uhrzeit_emoji2(self):
        message = self._new_message("⏰")
        triggered = TimeCommand.triggered(message, TimeCommand.triggers)
        self.assertEqual(triggered, True)

    def test_dont_trigger_hallowelt(self):
        message = self._new_message("Hallo Welt")
        triggered = TimeCommand.triggered(message, TimeCommand.triggers)
        self.assertEqual(triggered, False)

    def test_dont_trigger_none(self):
        message = self._new_message(None)
        triggered = TimeCommand.triggered(message, TimeCommand.triggers)
        self.assertEqual(triggered, False)

    def test_dont_trigger_emptystring(self):
        message = self._new_message("")
        triggered = TimeCommand.triggered(message, TimeCommand.triggers)
        self.assertEqual(triggered, False)


if __name__ == "__main__":
    unittest.main()
