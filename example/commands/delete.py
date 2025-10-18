import asyncio
from datetime import datetime

from signalbot import Command, Context, MessageType, triggered


class DeleteCommand(Command):
    @triggered("delete")
    async def handle(self, c: Context) -> None:
        timestamp = await c.send("This message will be deleted in two seconds.")
        await asyncio.sleep(2)
        await c.remote_delete(timestamp=timestamp)


class ReceiveDeleteCommand(Command):
    async def handle(self, c: Context) -> None:
        if c.message.type == MessageType.DELETE_MESSAGE:
            deleted_at = datetime.fromtimestamp(  # noqa: DTZ006
                c.message.remote_delete_timestamp / 1000
            )
            await c.send(f"You've deleted a message, which was sent at {deleted_at}.")
