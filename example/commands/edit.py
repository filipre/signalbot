import asyncio

from signalbot import Command, Context, triggered


class EditCommand(Command):
    @triggered("edit")
    async def handle(self, c: Context) -> None:
        timestamp = await c.send("This message will be edited in two seconds.")
        await asyncio.sleep(2)
        await c.edit("This message has been edited.", edit_timestamp=timestamp)
