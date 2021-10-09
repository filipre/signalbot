import asyncio
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from signal_api import SignalAPI
from .command import Command
from .message import Message, UnknownMessageFormatError


class SignalBot:
    def __init__(self, signal_service: str, phone_number: str, config: dict):
        self.signal_service = signal_service
        self.phone_number = phone_number
        self.config = config

        self.active_commands = []
        self.active_groups = {}
        self.scheduler = AsyncIOScheduler()

        self._signal = None
        self._q = None

    def listen(self, group: str, secret: str):
        self.active_groups[group] = secret

    def register(self, command: Command):
        command.bot = self
        command.init()
        self.active_commands.append(command)

    def start(self):
        # define signal after groups are fixed
        self._signal = SignalAPI(self.signal_service, self.phone_number)

        loop = asyncio.get_event_loop()
        loop.create_task(self._produce_consume_messages())

        # Add more scheduler tasks here...
        self.scheduler.start()

        # Run event loop
        loop.run_forever()

    async def send(self, group_id: str, text: str):
        if group_id not in self.active_groups:
            raise Exception(
                "group_id is not in self.groups. Something must have changed."
            )  # TODO
        receiver = self.active_groups[group_id]
        await self._signal.send(text, receiver)
        logging.info(f"[Bot] New message sent:\n{text}")

    async def reply(self, message: Message, text: str):
        group_id = message.group
        await self.send(group_id, text)

    async def react(self, message: Message, emoji: str):
        # TODO: replace this with the react endpoint
        await self.reply(message, emoji)

    async def _produce_consume_messages(self, producers=1, consumers=3) -> None:
        self._q = asyncio.Queue()
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
        async for raw_message in self._signal.receive():
            logging.info(f"[Raw Message] {raw_message}")

            try:
                message = Message.parse(raw_message)
            except UnknownMessageFormatError:
                continue

            group = message.group
            if group not in self.active_groups:
                continue

            for command in self.active_commands:
                await self._q.put((command, message, time.perf_counter()))

    async def _consume(self, name: int) -> None:
        logging.info(f"[Bot] Consumer #{name} started")
        while True:
            command, message, t = await self._q.get()
            now = time.perf_counter()
            logging.info(f"[Bot] Consumer #{name} got new job in {now-t:0.5f} seconds")

            # Handle Command
            try:
                await command.handle(message)
            except Exception as e:
                logging.error(f"[{command.__class__.__name__}] Error: {e}")
                continue

            # Done
            self._q.task_done()
