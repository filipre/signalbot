from signalbot import Command, Context


class EditCommand(Command):
    async def handle(self, c: Context):
        if "edit" in c.message.text.lower():
            await c.edit(
                "i read it now. i hope you're doing ok",
            )
