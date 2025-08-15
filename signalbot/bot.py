import asyncio
from collections import defaultdict
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import traceback
from typing import Any, TypeAlias, Literal
from collections.abc import Callable
import re
import uuid
import phonenumbers
import itertools
from packaging.version import Version

from signalbot.api import SignalAPI, ReceiveMessagesError
from signalbot.command import Command
from signalbot.message import Message, UnknownMessageFormatError
from signalbot.storage import RedisStorage, SQLiteStorage
from signalbot.context import Context
from signalbot.link_previews import LinkPreview

CommandList: TypeAlias = list[
    tuple[
        Command,
        list[str] | bool,
        list[str] | bool,
        Callable[[Message], bool] | None,
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
        download_attachments: True
        """
        self.config = config

        self._commands_to_be_registered: CommandList = []  # populated by .register()
        self.commands: CommandList = []  # populated by .start()

        self.groups = []  # populated by .start()
        self._groups_by_id = {}
        self._groups_by_internal_id = {}
        self._groups_by_name = defaultdict(list)

        try:
            self._phone_number = self.config["phone_number"]
            self._signal_service = self.config["signal_service"]
            download_attachments = self.config.get("download_attachments", True)
            self._signal = SignalAPI(
                self._signal_service, self._phone_number, download_attachments
            )
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

        config_storage = {}
        try:
            config_storage = self.config["storage"]
            if config_storage.get("type") == "sqlite":
                self._sqlite_db = config_storage["sqlite_db"]
                self.storage = SQLiteStorage(self._sqlite_db)
                logging.info("sqlite storage initilized")
            else:
                self._redis_host = config_storage["redis_host"]
                self._redis_port = config_storage["redis_port"]
                self.storage = RedisStorage(self._redis_host, self._redis_port)
                logging.info("redis storage initilized")
        except Exception:
            self.storage = SQLiteStorage()
            if config_storage.get("type") != "in-memory":
                logging.warning(
                    "[Bot] Could not initialize Redis and no SQLite DB name was given."
                    " In-memory storage will be used."
                    " Restarting will delete the storage!"
                    " Add storage: {'type': 'in-memory'}"
                    " to the config to silence this error."
                )
            if "redis_host" in config_storage:
                logging.warning(
                    f"[Bot] Redis initialization error: {traceback.format_exc()}"
                )

    def register(
        self,
        command: Command,
        contacts: list[str] | bool = True,
        groups: list[str] | bool = True,
        f: Callable[[Message], bool] | None = None,
    ) -> None:
        command.bot = self
        command.setup()
        self._commands_to_be_registered.append((command, contacts, groups, f))

    async def _resolve_commands(self) -> None:
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

    async def _async_post_init(self) -> None:
        await self._check_signal_service()
        await self._check_signal_cli_rest_api_version()
        await self._detect_groups()
        await self._resolve_commands()
        await self._produce_consume_messages()

    async def _check_signal_service(self) -> None:
        while (await self._signal.check_signal_service()) is False:
            logging.error("Cannot connect to the signal-cli-rest-api service, retrying")
            await asyncio.sleep(self.config.get("retry_interval", 1))

    async def _check_signal_cli_rest_api_version(self) -> None:
        min_version = Version("0.94.0")
        version = await self._signal.get_signal_cli_rest_api_version()
        if Version(version) < min_version:
            raise RuntimeError(
                f"Incompatible signal-cli-rest-api version, found {version}, minimum required is {min_version}"
            )

    def _store_reference_to_task(
        self, task: asyncio.Task, task_set: set[asyncio.Task]
    ) -> None:
        # Keep a hard reference to the tasks, fixes Ruff's RUF006 rule
        task_set.add(task)
        task.add_done_callback(task_set.discard)

    def start(self, run_forever: bool = True) -> None:
        task = self._event_loop.create_task(
            self._rerun_on_exception(self._async_post_init)
        )
        self._store_reference_to_task(task, self._running_tasks)

        if run_forever:
            # Add more scheduler tasks here
            # self.scheduler.add_job(...)
            self.scheduler.start()

            self._event_loop.run_forever()

    async def send(
        self,
        receiver: str,
        text: str,
        base64_attachments: list | None = None,
        link_preview: LinkPreview | None = None,
        quote_author: str | None = None,
        quote_mentions: list | None = None,
        quote_message: str | None = None,
        quote_timestamp: int | None = None,
        mentions: (
            list[dict[str, Any]] | None
        ) = None,  # [{ "author": "uuid" , "start": 0, "length": 1 }]
        edit_timestamp: int | None = None,
        text_mode: str = None,
    ) -> int:
        receiver = self._resolve_receiver(receiver)
        link_preview_raw = link_preview.model_dump() if link_preview else None

        resp = await self._signal.send(
            receiver,
            text,
            base64_attachments=base64_attachments,
            link_preview=link_preview_raw,
            quote_author=quote_author,
            quote_mentions=quote_mentions,
            quote_message=quote_message,
            quote_timestamp=quote_timestamp,
            mentions=mentions,
            text_mode=text_mode,
            edit_timestamp=edit_timestamp,
        )
        resp_payload = await resp.json()
        timestamp = int(resp_payload["timestamp"])
        logging.info(f"[Bot] New message {timestamp} sent:\n{text}")

        return timestamp

    async def react(self, message: Message, emoji: str) -> None:
        # TODO: check that emoji is really an emoji
        recipient = message.recipient()
        recipient = self._resolve_receiver(recipient)
        target_author = message.source
        timestamp = message.timestamp
        await self._signal.react(recipient, emoji, target_author, timestamp)
        logging.info(f"[Bot] New reaction: {emoji}")

    async def receipt(
        self, message: Message, receipt_type: Literal["read", "viewed"]
    ) -> None:
        if message.group is not None:
            logging.warning(f"[Bot] Receipts are not supported for groups")
            return

        recipient = self._resolve_receiver(message.recipient())
        await self._signal.receipt(recipient, receipt_type, message.timestamp)
        logging.info(f"[Bot] Receipt: {receipt_type}")

    async def start_typing(self, receiver: str) -> None:
        receiver = self._resolve_receiver(receiver)
        await self._signal.start_typing(receiver)

    async def stop_typing(self, receiver: str) -> None:
        receiver = self._resolve_receiver(receiver)
        await self._signal.stop_typing(receiver)

    async def update_contact(
        self,
        receiver: str,
        expiration_in_seconds: int | None = None,
        name: str | None = None,
    ) -> None:
        receiver = self._resolve_receiver(receiver)
        await self._signal.update_contact(
            receiver, expiration_in_seconds=expiration_in_seconds, name=name
        )

    async def update_group(
        self,
        group_id: str,
        base64_avatar: str | None = None,
        description: str | None = None,
        expiration_in_seconds: int | None = None,
        name: str | None = None,
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

    async def _detect_groups(self) -> None:
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

    def _is_valid_uuid(self, receiver_uuid: str) -> bool:
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

    def _get_group_by_name(self, group_name: str) -> dict[str, Any] | None:
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

    async def _produce_consume_messages(
        self, producers: int = 1, consumers: int = 3
    ) -> None:
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
        contacts: list[str] | bool,
        group_ids: list[str] | bool,
    ) -> bool:
        """Is the command activated for a certain chat or group?"""
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
        f: Callable[[Message], bool] | None = None,
    ) -> bool:
        if f is None:
            return True

        return f(message)

    async def _ask_commands_to_handle(self, message: Message) -> None:
        for command, contacts, group_ids, f in self.commands:
            if not self._should_react_for_contact(message, contacts, group_ids):
                continue

            if not self._should_react_for_lambda(message, f):
                continue

            if not command.is_appropriate(message):
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
