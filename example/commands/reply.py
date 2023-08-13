from signalbot import Command, Context


class ReplyCommand(Command):
    async def handle(self, c: Context):
        if "reply" in c.message.text.lower():
            await c.reply(
                "i ain't reading all that. i'm happy for u tho or sorry that happened"
            )
