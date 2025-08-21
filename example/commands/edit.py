from signalbot import Command, Context, triggered


class EditCommand(Command):
    @triggered(["edit"])
    async def handle(self, c: Context):
        timestamp = await c.reply("This message will be edited.")
        await c.edit("This message has been edited.", edit_timestamp=timestamp)
