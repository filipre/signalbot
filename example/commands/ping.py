from signalbot import Command, Context


class PingCommand(Command):
    def describe(self) -> str:
        return "🏓 Ping Command: Listen for a ping"

    async def handle(self, c: Context):
        command = c.message.text

        if command == "ping":
            await c.send("pong")
            return
