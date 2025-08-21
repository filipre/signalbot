from signalbot import Command, Context, triggered


class ReplyCommand(Command):
    @triggered(["reply"])
    async def handle(self, c: Context):  # noqa: ANN201
        await c.reply("This is a reply.")
