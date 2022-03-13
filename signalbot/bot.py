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
        scheduler:
            enable_jobstore: true
        """
        self.config = config
        self.commands = []
        self.groups = {}

        # Signal API (required)
        self._init_api()

        # Event loop (required)
        self._init_event_loop()

        # Storage (optional)
        self._init_storage()

        # Scheduler settings (jobstore)
        self._init_scheduler()

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
            logging.warn(
                "[Bot] Could not initialize Redis. In-memory storage will be used. "
                "Restarting will delete the storage!"
            )

    def _init_scheduler(self):
        # required: scheduler
        try:
            self.scheduler = AsyncIOScheduler(event_loop=self._event_loop)
        except Exception as e:
            raise SignalBotError(f"Could not initialize scheduler: {e}")

        # optional: jobstore option
        # TODO: do not use jobstore because it does not work with coroutines
        # try:
        #     enable_jobstore = self.config["scheduler"]["enable_jobstore"]
        #     if enable_jobstore is False:
        #         return
        #     if not isinstance(self.storage, RedisStorage):
        #         raise Exception("Scheduler is not Redis Storage")
        #     host, port = self._redis_host, self._redis_port
        #     self.scheduler.add_jobstore(
        #         "redis",
        #         jobs_key="Signalbot:scheduler:jobs",
        #         run_times_key="Signalbot:scheduler:run_times",
        #         host=host,
        #         port=port,
        #     )
        # except Exception as e:
        #     logging.warn(
        #         "[Bot] Could not enable scheduler's job store, despite setting "
        #         f"`enable_jobstore` to True: {e}"
        #     )
        #     return

    def listen(self, group: str, secret: str):
        self.groups[group] = secret

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
        receiver_secret = self._resolve_receiver(receiver)
        resp = await self._signal.send(
            receiver_secret, text, base64_attachments=base64_attachments
        )
        resp_payload = await resp.json()
        timestamp = resp_payload["timestamp"]
        logging.info(f"[Bot] New message {timestamp} sent:\n{text}")

        if listen:
            sent_message = Message(
                source=self._phone_number,
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
        recipient = self._resolve_receiver(message.group)
        target_author = message.source
        timestamp = message.timestamp
        await self._signal.react(recipient, emoji, target_author, timestamp)
        logging.info(f"[Bot] New reaction: {emoji}")

    async def start_typing(self, receiver: str):
        receiver_secret = self._resolve_receiver(receiver)
        await self._signal.start_typing(receiver_secret)

    async def stop_typing(self, receiver: str):
        receiver_secret = self._resolve_receiver(receiver)
        await self._signal.stop_typing(receiver_secret)

    def _resolve_receiver(self, receiver: str) -> str:
        # resolve receiver group id by using group secrets
        if receiver not in self.groups:
            raise SignalBotError("receiver is not in self.groups")
        receiver_secret = self.groups[receiver]

        return receiver_secret

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

                group = message.group
                if group not in self.groups:
                    continue

                await self._ask_commands_to_handle(message)

        except ReceiveMessagesError as e:
            # TODO: retry strategy
            raise SignalBotError(f"Cannot receive messages: {e}")

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
