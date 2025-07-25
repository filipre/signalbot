from signalbot import Command, Context


class EditCommand(Command):
    async def handle(self, c: Context):
        if "edit" in c.message.text.lower():
            timestamp = await c.send(
                "i ain't reading all that. i'm happy for u tho or sorry that happened"
            )
            await c.edit(
                "i read it now. i hope you're doing ok",
                timestamp=timestamp,
            )
