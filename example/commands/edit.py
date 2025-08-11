from signalbot import Command, Context


class EditCommand(Command):
    async def handle(self, c: Context):
        if c.message.text == "edit":
            timestamp = await c.reply("This message will be edited.")
            await c.edit("This message has been edited.", edit_timestamp=timestamp)
