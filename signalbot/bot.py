import asyncio
from collections import defaultdict
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import traceback
from typing import Optional, Union, List, Callable, Any, TypeAlias, Literal
import re
import uuid
import phonenumbers
import itertools

from .api import SignalAPI, ReceiveMessagesError
from .command import Command
from .message import Message, UnknownMessageFormatError
from .storage import RedisStorage, SQLiteStorage
from .context import Context

CommandList: TypeAlias = list[
    tuple[
        Command,
        Optional[Union[List[str], bool]],
        Optional[Union[List[str], bool]],
        Optional[Callable[[Message], bool]],
    ]
]


class SignalBot:
    def __init__(self, config: dict):
        """SignalBot

        Example Config:
        ======= Mandatory fields ========
        signal_service: "127.0.0.1:8080"
        phone_number: "+49123456789"

        ======= Optional fields ========
        storage:
            redis_host: "redis"
            redis_port: 6379
        retry_interval: 1
        """
        self.config = config

        self._commands_to_be_registered: CommandList = []  # populated by .register()
        self.commands: CommandList = []  # populated by .start()

        self.user_chats = set()  # deprecated
        self.group_chats = set()  # deprecated
        self._listen_mode_activated = False

        self.groups = []  # populated by .start()
        self._groups_by_id = {}
        self._groups_by_internal_id = {}
        self._groups_by_name = defaultdict(list)

        try:
            self._phone_number = self.config["phone_number"]
            self._signal_service = self.config["signal_service"]
            self._signal = SignalAPI(self._signal_service, self._phone_number)
        except KeyError:
            raise SignalBotError("Could not initialize SignalAPI with given config")

        self._event_loop = asyncio.get_event_loop()
        self._q = asyncio.Queue()
        self._running_tasks: set[asyncio.Task] = set()

        self._produce_tasks: set[asyncio.Task] = set()
        self._consume_tasks: set[asyncio.Task] = set()

        try:
            self.scheduler = AsyncIOScheduler(event_loop=self._event_loop)
        except Exception as e:
            raise SignalBotError(f"Could not initialize scheduler: {e}")

        try:
            config_storage = self.config["storage"]
            if config_storage.get("type") == "sqlite":
                self._sqlite_db = config_storage["sqlite_db"]
                self.storage = SQLiteStorage(self._sqlite_db)
            else:
                self._redis_host = config_storage["redis_host"]
                self._redis_port = config_storage["redis_port"]
                self.storage = RedisStorage(self._redis_host, self._redis_port)
        except Exception:
            self.storage = SQLiteStorage()
            logging.warning(
                "[Bot] Could not initialize Redis and no SQLite DB name was given."
                " In-memory storage will be used."
                " Restarting will delete the storage!"
            )

    # deprecated
    def listen(self, required_id: str, optional_id: str = None):
        logging.warning(
            "[Deprecation Warning] .listen is deprecated and will be removed in future versions. Please use .register"
        )

        # Case 1: required id is a phone number, optional_id is not being used
        if self._is_phone_number(required_id):
            phone_number = required_id
            self._listenUser(phone_number)
            return

        # Case 2: required id is a group id
        if self._is_group_id(required_id) and self._is_internal_id(optional_id):
            group_id = required_id
            internal_id = optional_id
            self._listenGroup(group_id, internal_id)
            return

        # Case 3: optional_id is a group id (Case 2 swapped)
        if self._is_internal_id(required_id) and self._is_group_id(optional_id):
            group_id = optional_id
            internal_id = required_id
            self._listenGroup(group_id, internal_id)
            return

        logging.warning(
            "[Bot] Can't listen for user/group because input does not look valid"
        )

    # deprecated
    def listenUser(self, phone_number: str):
        logging.warning(
            "[Deprecation Warning] .listenUser is deprecated and will be removed in future versions. Please use .register"
        )
        return self._listenUser(phone_number)

    # deprecated
    def _listenUser(self, phone_number: str):
        self._listen_mode_activated = True
        if not self._is_phone_number(phone_number):
            logging.warning(
                "[Bot] Can't listen for user because phone number does not look valid"
            )
            return

        self.user_chats.add(phone_number)

    # deprecated
    def listenGroup(self, group_id: str, internal_id: str = None):
        logging.warning(
            "[Deprecation Warning] .listenGroup is deprecated and will be removed in future versions. Please use .register"
        )
        return self._listenGroup(group_id, internal_id)

    # deprecated
    def _listenGroup(self, group_id: str, internal_id: str = None):
        self._listen_mode_activated = True
        if not (self._is_group_id(group_id) and self._is_internal_id(internal_id)):
            logging.warning(
                "[Bot] Can't listen for group because group id and "
                "internal id do not look valid"
            )
            return

        self.group_chats.add(internal_id)

    def register(
        self,
        command: Command,
        contacts: Optional[Union[List[str], bool]] = True,
        groups: Optional[Union[List[str], bool]] = True,
        f: Optional[Callable[[Message], bool]] = None,
    ):
        command.bot = self
        command.setup()
        self._commands_to_be_registered.append((command, contacts, groups, f))

    async def _resolve_commands(self):
        self.commands = []
        for command, contacts, groups, f in self._commands_to_be_registered:
            group_ids = None

            if isinstance(groups, bool):
                group_ids = groups

            if isinstance(groups, list):
                group_ids = []
                for group in groups:
                    if self._is_group_id(group):  # group is a group id, higher prio
                        group_ids.append(group)
                    else:  # group is a group name
                        matched_group = self._get_group_by_name(group)
                        if matched_group is not None:
                            group_ids.append(matched_group["id"])
                        else:
                            logging.warning(
                                f"[Bot] [{command.__class__.__name__}] '{group}' is not a valid group name or id"
                            )

            self.commands.append((command, contacts, group_ids, f))

    async def _async_post_init(self):
        await self._check_signal_service()
        await self._detect_groups()
        await self._resolve_commands()
        await self._produce_consume_messages()

    async def _check_signal_service(self):
        while (await self._signal.check_signal_service()) is False:
            logging.error("Cannot connect to the signal-cli-rest-api service, retrying")
            await asyncio.sleep(self.config.get("retry_interval", 1))

    def _store_reference_to_task(self, task: asyncio.Task, task_set: set[asyncio.Task]):
        # Keep a hard reference to the tasks, fixes Ruff's RUF006 rule
        task_set.add(task)
        task.add_done_callback(task_set.discard)

    def start(self):
        task = self._event_loop.create_task(
            self._rerun_on_exception(self._async_post_init)
        )
        self._store_reference_to_task(task, self._running_tasks)

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
        quote_author: str = None,
        quote_mentions: list = None,
        quote_message: str = None,
        quote_timestamp: str = None,
        mentions: (
            list[dict[str, Any]] | None
        ) = None,  # [{ "author": "uuid" , "start": 0, "length": 1 }]
        text_mode: str = None,
        listen: bool = False,
    ) -> str:
        receiver = self._resolve_receiver(receiver)
        resp = await self._signal.send(
            receiver,
            text,
            base64_attachments=base64_attachments,
            quote_author=quote_author,
            quote_mentions=quote_mentions,
            quote_message=quote_message,
            quote_timestamp=quote_timestamp,
            mentions=mentions,
            text_mode=text_mode,
        )
        resp_payload = await resp.json()
        timestamp = resp_payload["timestamp"]
        logging.info(f"[Bot] New message {timestamp} sent:\n{text}")

        if listen:
            logging.warning(f"[Bot] send(..., listen=True) is not supported anymore")

        return timestamp

    async def react(self, message: Message, emoji: str):
        # TODO: check that emoji is really an emoji
        recipient = message.recipient()
        recipient = self._resolve_receiver(recipient)
        target_author = message.source
        timestamp = message.timestamp
        await self._signal.react(recipient, emoji, target_author, timestamp)
        logging.info(f"[Bot] New reaction: {emoji}")

    async def receipt(self, message: Message, receipt_type: Literal["read", "viewed"]):
        if message.group is not None:
            logging.warning(f"[Bot] Receipts are not supported for groups")
            return

        recipient = self._resolve_receiver(message.recipient())
        await self._signal.receipt(recipient, receipt_type, message.timestamp)
        logging.info(f"[Bot] Receipt: {receipt_type}")

    async def start_typing(self, receiver: str):
        receiver = self._resolve_receiver(receiver)
        await self._signal.start_typing(receiver)

    async def stop_typing(self, receiver: str):
        receiver = self._resolve_receiver(receiver)
        await self._signal.stop_typing(receiver)

    async def update_contact(
        self,
        receiver: str,
        expiration_in_seconds: Optional[int] = None,
        name: Optional[str] = None,
    ) -> None:
        receiver = self._resolve_receiver(receiver)
        await self._signal.update_contact(
            receiver, expiration_in_seconds=expiration_in_seconds, name=name
        )

    async def update_group(
        self,
        group_id: str,
        base64_avatar: Optional[str] = None,
        description: Optional[str] = None,
        expiration_in_seconds: Optional[int] = None,
        name: Optional[str] = None,
    ) -> None:
        group_id = self._resolve_receiver(group_id)
        await self._signal.update_group(
            group_id,
            base64_avatar=base64_avatar,
            description=description,
            expiration_in_seconds=expiration_in_seconds,
            name=name,
        )

    async def delete_attachment(self, attachment_filename: str) -> None:
        # Delete the attachment from the local storage
        await self._signal.delete_attachment(attachment_filename)

    async def _detect_groups(self):
        # reset group lookups to avoid stale data
        self.groups = await self._signal.get_groups()

        self._groups_by_id: dict[str, dict[str, Any]] = {}
        self._groups_by_internal_id: dict[str, dict[str, Any]] = {}
        self._groups_by_name: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for group in self.groups:
            self._groups_by_id[group["id"]] = group
            self._groups_by_internal_id[group["internal_id"]] = group
            self._groups_by_name[group["name"]].append(group)

        logging.info(f"[Bot] {len(self.groups)} groups detected")

    def _resolve_receiver(self, receiver: str) -> str:
        if self._is_phone_number(receiver):
            return receiver

        if self._is_valid_uuid(receiver):
            return receiver

        if self._is_username(receiver):
            return receiver

        if self._is_group_id(receiver):
            return receiver

        group = self._groups_by_internal_id.get(receiver)
        if group is not None:
            return group["id"]

        group = self._get_group_by_name(receiver)
        if group is not None:
            return group["id"]

        raise SignalBotError(f"Cannot resolve receiver.")

    def _is_phone_number(self, phone_number: str) -> bool:
        try:
            parsed_number = phonenumbers.parse(phone_number, region=None)
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False

    def _is_valid_uuid(self, receiver_uuid: str):
        try:
            uuid.UUID(str(receiver_uuid))
            return True
        except ValueError:
            return False

    def _is_username(self, receiver_username: str) -> bool:
        """
        Check if username has correct format, as described in
        https://support.signal.org/hc/en-us/articles/6712070553754-Phone-Number-Privacy-and-Usernames#username_req
        Additionally, cannot have more than 9 digits and the digits cannot be 00.
        """
        split_username = receiver_username.split(".")
        if len(split_username) == 2:
            characters = split_username[0]
            digits = split_username[1]
            if len(characters) < 3 or len(characters) > 32:
                return False
            if not re.match(r"^[A-Za-z\d_]+$", characters):
                return False
            if len(digits) < 2 or len(digits) > 9:
                return False
            try:
                digits = int(digits)
                if digits == 0:
                    return False
                return True
            except ValueError:
                return False
        else:
            return False

    def _is_group_id(self, group_id: str) -> bool:
        """Check if group_id has the right format, e.g.

              random string                                              length 66
              ↓                                                          ↓
        group.OyZzqio1xDmYiLsQ1VsqRcUFOU4tK2TcECmYt2KeozHJwglMBHAPS7jlkrm=
        ↑                                                                ↑
        prefix                                                           suffix
        """
        if group_id is None:
            return False

        return re.match(r"^group\.[a-zA-Z0-9]{59}=$", group_id)

    def _is_internal_id(self, internal_id: str) -> bool:
        if internal_id is None:
            return False
        return internal_id[-1] == "="

    def _get_group_by_name(self, group_name: str) -> Optional[dict[str, Any]]:
        groups = self._groups_by_name.get(group_name)
        if groups is not None:
            if len(groups) > 1:
                logging.warning(
                    f"[Bot] There is more than one group named '{group_name}', using the first one."
                )
            return groups[0]
        return None

    # see https://stackoverflow.com/questions/55184226/catching-exceptions-in-individual-tasks-and-restarting-them
    @classmethod
    async def _rerun_on_exception(cls, coro, *args, **kwargs):
        """Restart coroutine by waiting an exponential time deplay"""
        max_sleep = 5 * 60  # sleep for at most 5 mins until rerun
        reset = 3 * 60  # reset after 3 minutes running successfully
        init_sleep = 1  # always start with sleeping for 1 second

        next_sleep = init_sleep
        while True:
            start_t = int(time.monotonic())  # seconds

            try:
                return await coro(*args, **kwargs)
            except asyncio.CancelledError:
                raise
            except Exception:
                traceback.print_exc()

            end_t = int(time.monotonic())  # seconds

            if end_t - start_t < reset:
                sleep_t = next_sleep
                next_sleep = min(max_sleep, next_sleep * 2)  # double sleep time
            else:
                next_sleep = init_sleep  # reset sleep time
                sleep_t = next_sleep

            logging.warning(f"Restarting coroutine in {sleep_t} seconds")
            await asyncio.sleep(sleep_t)

    async def _produce_consume_messages(self, producers=1, consumers=3) -> None:
        for task in itertools.chain(self._consume_tasks, self._produce_tasks):
            task.cancel()

        self._produce_tasks.clear()

        for n in range(1, producers + 1):
            produce_task = self._rerun_on_exception(self._produce, n)
            produce_task = asyncio.create_task(produce_task)
            self._store_reference_to_task(produce_task, self._produce_tasks)

        self._consume_tasks.clear()

        for n in range(1, consumers + 1):
            consume_task = self._rerun_on_exception(self._consume, n)
            consume_task = asyncio.create_task(consume_task)
            self._store_reference_to_task(consume_task, self._consume_tasks)

    async def _produce(self, name: int) -> None:
        logging.info(f"[Bot] Producer #{name} started")
        try:
            async for raw_message in self._signal.receive():
                logging.info(f"[Raw Message] {raw_message}")

                try:
                    message = await Message.parse(self._signal, raw_message)
                except UnknownMessageFormatError:
                    continue

                # Update groups if message is from an unknown group
                if (
                    message.is_group()
                    and self._groups_by_internal_id.get(message.group) is None
                ):
                    await self._detect_groups()

                await self._ask_commands_to_handle(message)

        except ReceiveMessagesError as e:
            # TODO: retry strategy
            raise SignalBotError(f"Cannot receive messages: {e}")

    def _should_react_for_contact(
        self,
        message: Message,
        contacts: Union[list[str], bool],
        group_ids: Union[list[str], bool],
    ):
        """Is the command activated for a certain chat or group?"""

        # Deprected Case: Listen Mode
        if self._listen_mode_activated:
            if message.is_private() and message.source in self.user_chats:
                return True

            if message.is_group() and message.group in self.group_chats:
                return True

            return False

        # Case 1: Private message
        if message.is_private():
            # a) registered for all numbers
            if isinstance(contacts, bool) and contacts:
                return True

            # b) whitelisted numbers
            if isinstance(contacts, list) and message.source in contacts:
                return True

        # Case 2: Group message
        if message.is_group():
            # a) registered for all groups
            if isinstance(group_ids, bool) and group_ids:
                return True

            # b) whitelisted group ids
            group_id = self._groups_by_internal_id.get(message.group, {}).get("id")
            if isinstance(group_ids, list) and group_id and group_id in group_ids:
                return True

        return False

    def _should_react_for_lambda(
        self,
        message: Message,
        f: Optional[Callable[[Message], bool]] = None,
    ) -> bool:
        if f is None:
            return True

        return f(message)

    async def _ask_commands_to_handle(self, message: Message):
        for command, contacts, group_ids, f in self.commands:
            if not self._should_react_for_contact(message, contacts, group_ids):
                continue

            if not self._should_react_for_lambda(message, f):
                continue

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
            for log in "".join(traceback.format_exception(e)).rstrip().split("\n"):
                logging.error(f"[{command.__class__.__name__}]: {log}")
            raise e

        # done
        self._q.task_done()


class SignalBotError(Exception):
    pass
