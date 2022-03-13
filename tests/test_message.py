import unittest
from signalbot import Message, MessageType


class TestMessage(unittest.TestCase):
    raw_sync_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"syncMessage":{"sentMessage":{"timestamp":1632576001632,"message":"Uhrzeit","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"<groupid>","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa
    raw_data_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"dataMessage":{"timestamp":1632576001632,"message":"Uhrzeit","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"<groupid>","type":"DELIVER"}}}}'  # noqa
    raw_reaction_message = '{"envelope":{"source":"<source>","sourceNumber":"<source>","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"syncMessage":{"sentMessage":{"timestamp":1632576001632,"message":null,"expiresInSeconds":0,"viewOnce":false,"reaction":{"emoji":"👍","targetAuthor":"<target>","targetAuthorNumber":"<target>","targetAuthorUuid":"<uuid>","targetSentTimestamp":1632576001632,"isRemove":false},"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"<groupid>","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa
    raw_user_chat_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"dataMessage":{"timestamp":1632576001632,"message":"Uhrzeit","expiresInSeconds":0,"viewOnce":false}},"account":"+49987654321","subscription":0}'  # noqa

    expected_source = "+490123456789"
    expected_timestamp = 1632576001632
    expected_text = "Uhrzeit"
    expected_group = "<groupid>"

    # Own Message
    def test_parse_source_own_message(self):
        message = Message.parse(TestMessage.raw_sync_message)
        self.assertEqual(message.timestamp, TestMessage.expected_timestamp)

    def test_parse_timestamp_own_message(self):
        message = Message.parse(TestMessage.raw_sync_message)
        self.assertEqual(message.source, TestMessage.expected_source)

    def test_parse_type_own_message(self):
        message = Message.parse(TestMessage.raw_sync_message)
        self.assertEqual(message.type, MessageType.SYNC_MESSAGE)

    def test_parse_text_own_message(self):
        message = Message.parse(TestMessage.raw_sync_message)
        self.assertEqual(message.text, TestMessage.expected_text)

    def test_parse_group_own_message(self):
        message = Message.parse(TestMessage.raw_sync_message)
        self.assertEqual(message.group, TestMessage.expected_group)

    # Foreign Messages
    def test_parse_source_foreign_message(self):
        message = Message.parse(TestMessage.raw_data_message)
        self.assertEqual(message.timestamp, TestMessage.expected_timestamp)

    def test_parse_timestamp_foreign_message(self):
        message = Message.parse(TestMessage.raw_data_message)
        self.assertEqual(message.source, TestMessage.expected_source)

    def test_parse_type_foreign_message(self):
        message = Message.parse(TestMessage.raw_data_message)
        self.assertEqual(message.type, MessageType.DATA_MESSAGE)

    def test_parse_text_foreign_message(self):
        message = Message.parse(TestMessage.raw_data_message)
        self.assertEqual(message.text, TestMessage.expected_text)

    def test_parse_group_foreign_message(self):
        message = Message.parse(TestMessage.raw_data_message)
        self.assertEqual(message.group, TestMessage.expected_group)

    def test_read_reaction(self):
        message = Message.parse(TestMessage.raw_reaction_message)
        self.assertEqual(message.reaction, "👍")

    # User Chats
    def test_parse_user_chat_message(self):
        message = Message.parse(TestMessage.raw_user_chat_message)
        self.assertEqual(message.source, TestMessage.expected_source)
        self.assertEqual(message.text, TestMessage.expected_text)
        self.assertEqual(message.timestamp, TestMessage.expected_timestamp)
        self.assertIsNone(message.group)


if __name__ == "__main__":
    unittest.main()
