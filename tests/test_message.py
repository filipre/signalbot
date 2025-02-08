import base64
import unittest
from unittest.mock import AsyncMock, patch, Mock
import aiohttp
from signalbot import Message, MessageType
from signalbot.api import SignalAPI
from signalbot.utils import ChatTestCase, SendMessagesMock, ReceiveMessagesMock


class TestMessage(unittest.IsolatedAsyncioTestCase):
    raw_sync_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"syncMessage":{"sentMessage":{"timestamp":1632576001632,"message":"Uhrzeit","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"<groupid>","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa
    raw_data_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"dataMessage":{"timestamp":1632576001632,"message":"Uhrzeit","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"<groupid>","type":"DELIVER"}}}}'  # noqa
    raw_reaction_message = '{"envelope":{"source":"<source>","sourceNumber":"<source>","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"syncMessage":{"sentMessage":{"timestamp":1632576001632,"message":null,"expiresInSeconds":0,"viewOnce":false,"reaction":{"emoji":"👍","targetAuthor":"<target>","targetAuthorNumber":"<target>","targetAuthorUuid":"<uuid>","targetSentTimestamp":1632576001632,"isRemove":false},"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"<groupid>","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa
    raw_user_chat_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"dataMessage":{"timestamp":1632576001632,"message":"Uhrzeit","expiresInSeconds":0,"viewOnce":false}},"account":"+49987654321","subscription":0}'  # noqa
    raw_attachment_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"dataMessage":{"timestamp":1632576001632,"message":"Uhrzeit","expiresInSeconds":0,"viewOnce":false, "attachments": [{"contentType": "image/png", "filename": "image.png", "id": "1qeCjjWOOo9Gxv8pfdCw.png","size": 12005}]}},"account":"+49987654321","subscription":0}'  # noqa

    expected_source = "+490123456789"
    expected_timestamp = 1632576001632
    expected_text = "Uhrzeit"
    expected_group = "<groupid>"
    expected_local_filename = "1qeCjjWOOo9Gxv8pfdCw.png"

    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    group_id = "group_id1"
    group_secret = "group.group_secret1"
    groups = {group_id: group_secret}

    def setUp(self):
        self.signal_api = SignalAPI(
            TestMessage.signal_service, TestMessage.phone_number
        )

    # Own Message
    async def test_parse_source_own_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_sync_message)
        self.assertEqual(message.timestamp, TestMessage.expected_timestamp)

    async def test_parse_timestamp_own_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_sync_message)
        self.assertEqual(message.source, TestMessage.expected_source)

    async def test_parse_type_own_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_sync_message)
        self.assertEqual(message.type, MessageType.SYNC_MESSAGE)

    async def test_parse_text_own_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_sync_message)
        self.assertEqual(message.text, TestMessage.expected_text)

    async def test_parse_group_own_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_sync_message)
        self.assertEqual(message.group, TestMessage.expected_group)

    # Foreign Messages
    async def test_parse_source_foreign_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_data_message)
        self.assertEqual(message.timestamp, TestMessage.expected_timestamp)

    async def test_parse_timestamp_foreign_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_data_message)
        self.assertEqual(message.source, TestMessage.expected_source)

    async def test_parse_type_foreign_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_data_message)
        self.assertEqual(message.type, MessageType.DATA_MESSAGE)

    async def test_parse_text_foreign_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_data_message)
        self.assertEqual(message.text, TestMessage.expected_text)

    async def test_parse_group_foreign_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_data_message)
        self.assertEqual(message.group, TestMessage.expected_group)

    async def test_read_reaction(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_reaction_message)
        self.assertEqual(message.reaction, "👍")

    @patch("aiohttp.ClientSession.get", new_callable=AsyncMock)
    async def test_attachments(self, mock_get):
        attachment_bytes_str = b"test"

        mock_response = AsyncMock(spec=aiohttp.ClientResponse)
        mock_response.raise_for_status = Mock()
        mock_response.content.read = AsyncMock(return_value=attachment_bytes_str)

        mock_get.return_value = mock_response

        expected_base64_bytes = base64.b64encode(attachment_bytes_str)
        expected_base64_str = str(expected_base64_bytes, encoding="utf-8")

        message = await Message.parse(
            self.signal_api, TestMessage.raw_attachment_message
        )
        self.assertEqual(message.base64_attachments, [expected_base64_str])

        self.assertEqual(len(message.attachments_local_filenames), 1)
        self.assertEqual(
            message.attachments_local_filenames[0], TestMessage.expected_local_filename
        )

    # User Chats
    async def test_parse_user_chat_message(self):
        message = await Message.parse(
            self.signal_api, TestMessage.raw_user_chat_message
        )
        self.assertEqual(message.source, TestMessage.expected_source)
        self.assertEqual(message.text, TestMessage.expected_text)
        self.assertEqual(message.timestamp, TestMessage.expected_timestamp)
        self.assertIsNone(message.group)


if __name__ == "__main__":
    unittest.main()
