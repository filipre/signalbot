import base64

import aiohttp
import pytest
from pytest_mock import MockerFixture

from signalbot import Message, MessageType
from signalbot.api import SignalAPI


class TestMessage:
    raw_sync_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"syncMessage":{"sentMessage":{"timestamp":1632576001632,"message":"Uhrzeit","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"<groupid>","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa: E501
    raw_data_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"dataMessage":{"timestamp":1632576001632,"message":"Uhrzeit","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"<groupid>","type":"DELIVER"}}}}'  # noqa: E501
    raw_reaction_message = '{"envelope":{"source":"<source>","sourceNumber":"<source>","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"syncMessage":{"sentMessage":{"timestamp":1632576001632,"message":null,"expiresInSeconds":0,"viewOnce":false,"reaction":{"emoji":"👍","targetAuthor":"<target>","targetAuthorNumber":"<target>","targetAuthorUuid":"<uuid>","targetSentTimestamp":1632576001632,"isRemove":false},"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"<groupid>","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'  # noqa: E501
    raw_user_chat_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"dataMessage":{"timestamp":1632576001632,"message":"Uhrzeit","expiresInSeconds":0,"viewOnce":false}},"account":"+49987654321","subscription":0}'  # noqa: E501
    raw_attachment_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"dataMessage":{"timestamp":1632576001632,"message":"Uhrzeit","expiresInSeconds":0,"viewOnce":false, "attachments": [{"contentType": "image/png", "filename": "image.png", "id": "1qeCjjWOOo9Gxv8pfdCw.png","size": 12005}]}},"account":"+49987654321","subscription":0}'  # noqa: E501
    raw_preview_no_image_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"serverReceivedTimestamp":1632576001632,"serverDeliveredTimestamp":1632576001632,"dataMessage":{"timestamp":1632576001632,"message":"https://example.com is nice","expiresInSeconds":0,"viewOnce":false,"previews":[{"url":"https://example.com","title":"Example.com - Super example","description":"","image":null}],"account":"+41774289587"}}}'  # noqa: E501
    raw_user_read_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"serverReceivedTimestamp":1632576001632,"serverDeliveredTimestamp":1632576001632,"syncMessage":{"readMessages":[{"sender":"+49987654321","senderNumber":"+49987654321","senderUuid":"<uuid>","timestamp":1632576001632}]}},"account":"+49987654321"}'  # noqa: E501
    raw_group_update_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1768100104294,"serverReceivedTimestamp":1768100103544,"serverDeliveredTimestamp":1768100103588,"dataMessage":{"timestamp":1768100104294,"message":null,"expiresInSeconds":86400,"isExpirationUpdate":false,"viewOnce":false,"groupInfo":{"groupId":"<groupid>","groupName":"<name>","revision":100,"type":"UPDATE"}}},"account":"+49987654321"}'  # noqa: E501

    expected_source = "+490123456789"
    expected_timestamp = 1632576001632
    expected_text = "Uhrzeit"
    expected_group = "<groupid>"
    expected_local_filename = "1qeCjjWOOo9Gxv8pfdCw.png"

    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    group_id = "group_id1"
    group_secret = "group.group_secret1"  # noqa: S105
    groups = {group_id: group_secret}  # noqa: RUF012

    @pytest.fixture(autouse=True)
    def setup(self):
        self.signal_api = SignalAPI(
            TestMessage.signal_service,
            TestMessage.phone_number,
        )

    # Own Message
    @pytest.mark.asyncio
    async def test_parse_source_own_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_sync_message)
        assert message.timestamp == TestMessage.expected_timestamp

    @pytest.mark.asyncio
    async def test_parse_timestamp_own_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_sync_message)
        assert message.source == TestMessage.expected_source

    @pytest.mark.asyncio
    async def test_parse_type_own_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_sync_message)
        assert message.type == MessageType.SYNC_MESSAGE

    @pytest.mark.asyncio
    async def test_parse_text_own_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_sync_message)
        assert message.text == TestMessage.expected_text

    @pytest.mark.asyncio
    async def test_parse_group_own_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_sync_message)
        assert message.group == TestMessage.expected_group

    # Foreign Messages
    @pytest.mark.asyncio
    async def test_parse_source_foreign_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_data_message)
        assert message.timestamp == TestMessage.expected_timestamp

    @pytest.mark.asyncio
    async def test_parse_timestamp_foreign_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_data_message)
        assert message.source == TestMessage.expected_source

    @pytest.mark.asyncio
    async def test_parse_type_foreign_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_data_message)
        assert message.type == MessageType.DATA_MESSAGE

    @pytest.mark.asyncio
    async def test_parse_text_foreign_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_data_message)
        assert message.text == TestMessage.expected_text

    @pytest.mark.asyncio
    async def test_parse_group_foreign_message(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_data_message)
        assert message.group == TestMessage.expected_group

    @pytest.mark.asyncio
    async def test_read_reaction(self):
        message = await Message.parse(self.signal_api, TestMessage.raw_reaction_message)
        assert message.reaction == "👍"

    @pytest.mark.asyncio
    async def test_group_update(self):
        message = await Message.parse(
            self.signal_api, TestMessage.raw_group_update_message
        )
        assert message.updated_group_id == TestMessage.expected_group

    @pytest.mark.asyncio
    async def test_attachments(self, mocker: MockerFixture):
        attachment_bytes_str = b"test"

        mock_response = mocker.AsyncMock(spec=aiohttp.ClientResponse)
        mock_response.raise_for_status = mocker.Mock()
        mock_response.content.read = mocker.AsyncMock(return_value=attachment_bytes_str)

        mock_session = mocker.AsyncMock()
        mock_session.get = mocker.AsyncMock(return_value=mock_response)
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        mocker.patch("aiohttp.ClientSession", return_value=mock_session)

        expected_base64_bytes = base64.b64encode(attachment_bytes_str)
        expected_base64_str = str(expected_base64_bytes, encoding="utf-8")

        message = await Message.parse(
            self.signal_api,
            TestMessage.raw_attachment_message,
        )
        assert message.base64_attachments == [expected_base64_str]

        assert len(message.attachments_local_filenames) == 1
        assert (
            message.attachments_local_filenames[0]
            == TestMessage.expected_local_filename
        )

    # User Chats
    @pytest.mark.asyncio
    async def test_parse_user_chat_message(self):
        message = await Message.parse(
            self.signal_api,
            TestMessage.raw_user_chat_message,
        )
        assert message.source == TestMessage.expected_source
        assert message.text == TestMessage.expected_text
        assert message.timestamp == TestMessage.expected_timestamp
        assert message.group is None

    @pytest.mark.asyncio
    async def test_preview_no_image(self):
        message = await Message.parse(
            self.signal_api, TestMessage.raw_preview_no_image_message
        )
        assert isinstance(message.link_previews, list)
        assert len(message.link_previews) == 1

        lp = message.link_previews[0]
        assert lp.id is None
        assert lp.base64_thumbnail is None
        assert lp.url == "https://example.com"
        assert lp.title == "Example.com - Super example"
        assert lp.description == ""

    @pytest.mark.asyncio
    async def test_message_read(self):
        message = await Message.parse(
            self.signal_api, TestMessage.raw_user_read_message
        )

        assert message.type == MessageType.READ_MESSAGE
        assert message.text == ""
        assert isinstance(message.read_messages, list)
        assert len(message.read_messages) == 1

        rm = message.read_messages[0]
        assert rm.get("sender") == "+49987654321"
        assert rm.get("senderNumber") == "+49987654321"
        assert rm.get("timestamp") == TestMessage.expected_timestamp
        assert "senderUuid" in rm
