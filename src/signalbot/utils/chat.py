import unittest
import uuid
import time
import json
from ..bot import SignalBot


class ChatTestCase(unittest.IsolatedAsyncioTestCase):
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    group_id = "group_id1"
    group_secret = "group.group_secret1"
    config = {
        "signal_service": signal_service,
        "phone_number": phone_number,
    }

    def setUp(self):
        self.signal_bot = SignalBot(ChatTestCase.config)
        self.signal_bot.listen(ChatTestCase.group_id, ChatTestCase.group_secret)

    async def run_bot(self):
        PRODUCER_ID = 1337
        HANDLER_ID = 4444
        await self.signal_bot._produce(PRODUCER_ID)
        while self.signal_bot._q.qsize() > 0:
            await self.signal_bot._consume_new_item(HANDLER_ID)

    @classmethod
    def new_message(cls, text) -> str:
        timestamp = time.time()
        new_uuid = str(uuid.uuid4())
        message = {
            "envelope": {
                "source": ChatTestCase.phone_number,
                "sourceNumber": ChatTestCase.phone_number,
                "sourceUuid": new_uuid,
                "sourceName": "some_source_name",
                "sourceDevice": 1,
                "timestamp": timestamp,
                "syncMessage": {
                    "sentMessage": {
                        "timestamp": timestamp,
                        "message": text,
                        "expiresInSeconds": 0,
                        "viewOnce": False,
                        "mentions": [],
                        "attachments": [],
                        "contacts": [],
                        "groupInfo": {
                            "groupId": ChatTestCase.group_id,
                            "type": "DELIVER",
                        },
                        "destination": None,
                        "destinationNumber": None,
                        "destinationUuid": None,
                    }
                },
            }
        }
        return json.dumps(message)
