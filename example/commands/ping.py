from signalbot import Command, Context, triggered


class PingCommand(Command):
    def describe(self) -> str:
        return "🏓 Ping Command: Listen for a ping"

    @triggered(["ping"])
    async def handle(self, c: Context):  # noqa: ANN201
        await c.send("pong")
