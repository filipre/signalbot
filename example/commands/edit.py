import asyncio

from example.commands.help import CommandWithHelpMessage
from signalbot import Context, triggered


class EditCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "edit: ✏️ Edit a message."

    @triggered("edit")
    async def handle(self, c: Context) -> None:
        timestamp = await c.send("This message will be edited in two seconds.")
        await asyncio.sleep(2)
        await c.edit("This message has been edited.", timestamp)
