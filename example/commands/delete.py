from signalbot import Command, Context, triggered


class DeleteCommand(Command):
    @triggered(["delete"])
    async def handle(self, c: Context):  # noqa: ANN201
        timestamp = await c.reply("This message will be deleted.")
        await c.remote_delete(timestamp=timestamp)
