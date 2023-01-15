import asyncio
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging


from .api import SignalAPI, ReceiveMessagesError
from .command import Command
from .message import Message, UnknownMessageFormatError, MessageType
from .storage import RedisStorage, InMemoryStorage
from .context import Context


class SignalBot:
    def __init__(self, config: dict):
        """SignalBot

        Example Config:
        ===============
        signal_service: "127.0.0.1:8080"
        phone_number: "+49123456789"
        storage:
            redis_host: "redis"
            redis_port: 6379
        """
        self.config = config

        self.commands = []  # populated by .register()

        self.user_chats = set()  # populated by .listenUser()
        self.listening_all_users = False

        self.group_chats = {}  # populated by .listenGroup()
        self.listening_all_groups = False

        # Required
        self._init_api()
        self._init_event_loop()
        self._init_scheduler()

        # Optional
        self._init_storage()

        # TODO
        self._event_loop.create_task(self._refresh_groups())
        # asyncio.run(self._refresh_groups())

    def _init_api(self):
        try:
            self._phone_number = self.config["phone_number"]
            self._signal_service = self.config["signal_service"]
            self._signal = SignalAPI(self._signal_service, self._phone_number)
        except KeyError:
            raise SignalBotError("Could not initialize SignalAPI with given config")

    def _init_event_loop(self):
        self._event_loop = asyncio.get_event_loop()
        self._q = asyncio.Queue()

    def _init_storage(self):
        try:
            config_storage = self.config["storage"]
            self._redis_host = config_storage["redis_host"]
            self._redis_port = config_storage["redis_port"]
            self.storage = RedisStorage(self._redis_host, self._redis_port)
        except Exception:
            self.storage = InMemoryStorage()
            logging.warning(
                "[Bot] Could not initialize Redis. In-memory storage will be used. "
                "Restarting will delete the storage!"
            )

    def _init_scheduler(self):
        try:
            self.scheduler = AsyncIOScheduler(event_loop=self._event_loop)
        except Exception as e:
            raise SignalBotError(f"Could not initialize scheduler: {e}")

    async def _refresh_groups(self):
        groups_json = await self._signal.list_groups()
        self._groups = {g["id"]: g["internal_id"] for g in groups_json}

    def listen(self, required_id: str, optional_id: str = None):
        # Case 1: required id is a phone number, optional_id is not being used
        if self._is_phone_number(required_id):
            phone_number = required_id
            self.listenUser(phone_number)
            return

        # Case 2: required id is a group id
        if self._is_group_id(required_id):
            self.listenGroup(required_id)
            return

        # Case 3: optional_id is a group id (Case 2 swapped)
        if self._is_internal_id(required_id) and self._is_group_id(optional_id):
            self.listenGroup(optional_id)
            return

        logging.warning(
            "[Bot] Can't listen for user/group because input does not look valid"
        )

    def listenUser(self, phone_number: str):
        if not self._is_phone_number(phone_number):
            logging.warning(
                "[Bot] Can't listen for user because phone number does not look valid"
            )
            return
        self.user_chats.add(phone_number)

    def listenAllUsers(self):
        self.listening_all_users = True

    def listenGroup(self, group_id: str):
        if group_id not in self._groups:
            logging.warning(
                "[Bot] Can't listen for group because group id does not seem valid"
            )
            return
        internal_id = self._groups[group_id]
        self.group_chats[internal_id] = group_id

    def listenAllGroups(self):
        self.listening_all_groups = True
        for group_id in self._groups:
            self.listenGroup(group_id)

    def _is_phone_number(self, phone_number: str) -> bool:
        if phone_number is None:
            return False
        return phone_number[0] == "+"

    def _is_group_id(self, group_id: str) -> bool:
        if group_id is None:
            return False
        prefix = "group."
        if group_id[: len(prefix)] != prefix:
            return False
        if group_id[-1] != "=":
            return False
        return True

    def _is_internal_id(self, internal_id: str) -> bool:
        if internal_id is None:
            return False
        return internal_id[-1] == "="

    def register(self, command: Command):
        command.bot = self
        command.setup()
        self.commands.append(command)

    def start(self):
        self._event_loop.create_task(self._produce_consume_messages())

        # Add more scheduler tasks here
        # self.scheduler.add_job(...)
        self.scheduler.start()

        # Run event loop
        self._event_loop.run_forever()

    async def send(
        self,
        receiver: str,
        text: str,
        base64_attachments: list = None,
        listen: bool = False,
    ) -> int:
        resolved_receiver = self._resolve_receiver(receiver)
        resp = await self._signal.send(
            resolved_receiver, text, base64_attachments=base64_attachments
        )
        resp_payload = await resp.json()
        timestamp = resp_payload["timestamp"]
        logging.info(f"[Bot] New message {timestamp} sent:\n{text}")

        if listen:
            if self._is_phone_number(receiver):
                sent_message = Message(
                    source=receiver,  # otherwise we can't respond in the right chat
                    timestamp=timestamp,
                    type=MessageType.SYNC_MESSAGE,
                    text=text,
                    base64_attachments=base64_attachments,
                    group=None,
                )
            else:
                sent_message = Message(
                    source=self._phone_number,  # no need to pretend
                    timestamp=timestamp,
                    type=MessageType.SYNC_MESSAGE,
                    text=text,
                    base64_attachments=base64_attachments,
                    group=receiver,
                )
            await self._ask_commands_to_handle(sent_message)

        return timestamp

    async def react(self, message: Message, emoji: str):
        # TODO: check that emoji is really an emoji
        recipient = self._resolve_receiver(message.recipient())
        target_author = message.source
        timestamp = message.timestamp
        await self._signal.react(recipient, emoji, target_author, timestamp)
        logging.info(f"[Bot] New reaction: {emoji}")

    async def start_typing(self, receiver: str):
        receiver = self._resolve_receiver(receiver)
        await self._signal.start_typing(receiver)

    async def stop_typing(self, receiver: str):
        receiver = self._resolve_receiver(receiver)
        await self._signal.stop_typing(receiver)

    def _resolve_receiver(self, receiver: str) -> str:
        if self._is_phone_number(receiver):
            return receiver

        if receiver in self.group_chats:
            internal_id = receiver
            group_id = self.group_chats[internal_id]
            return group_id

        raise SignalBotError(
            f"receiver {receiver} is not a phone number and not in self.group_chats. "
            "This should never happen."
        )

    async def _produce_consume_messages(self, producers=1, consumers=3) -> None:
        producers = [
            asyncio.create_task(self._produce(n)) for n in range(1, producers + 1)
        ]
        consumers = [
            asyncio.create_task(self._consume(n)) for n in range(1, consumers + 1)
        ]
        await asyncio.gather(*producers)
        await self._q.join()
        for c in consumers:
            c.cancel()

    async def _produce(self, name: int) -> None:
        logging.info(f"[Bot] Producer #{name} started")
        try:
            async for raw_message in self._signal.receive():
                logging.info(f"[Raw Message] {raw_message}")

                try:
                    message = Message.parse(raw_message)
                except UnknownMessageFormatError:
                    continue

                if not await self._should_handle(message):
                    continue

                await self._ask_commands_to_handle(message)

        except ReceiveMessagesError as e:
            # TODO: retry strategy
            raise SignalBotError(f"Cannot receive messages: {e}")

    async def _should_handle(self, message: Message) -> bool:
        # Case 1: Message is a group message
        if message.group:
            if message.group in self.group_chats:
                return True

            if not self.listening_all_groups:
                return False

            # we are listening to all groups
            # but we found a group internal_id that is not in self.group_chats
            # that means, it must have been created after the bots initialization
            # and we need to refresh self.group_chats
            # this should not happen very often and we can even sync groups every
            # hour to prevent delays further
            await self._refresh_groups()
            self.listenAllGroups()
            if message.group in self.group_chats:
                return True

            logging.info("[Bot] Something went horribly wrong with group listening")
            return False

        # Case 2: Message is a user message
        if self.listening_all_users:
            return True

        if message.source in self.user_chats:
            return True

        return False

    async def _ask_commands_to_handle(self, message: Message):
        for command in self.commands:
            await self._q.put((command, message, time.perf_counter()))

    async def _consume(self, name: int) -> None:
        logging.info(f"[Bot] Consumer #{name} started")
        while True:
            try:
                await self._consume_new_item(name)
            except Exception:
                continue

    async def _consume_new_item(self, name: int) -> None:
        command, message, t = await self._q.get()
        now = time.perf_counter()
        logging.info(f"[Bot] Consumer #{name} got new job in {now-t:0.5f} seconds")

        # handle Command
        try:
            context = Context(self, message)
            await command.handle(context)
        except Exception as e:
            logging.error(f"[{command.__class__.__name__}] Error: {e}")
            raise e

        # done
        self._q.task_done()


class SignalBotError(Exception):
    pass
