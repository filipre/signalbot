from signalbot import Command, Context


class PingCommand(Command):
    def describe(self) -> str:
        return "🏓 Ping Command: Listen for a ping"

    def is_appropriate(self, message) -> bool:
        return message.text == "ping"

    async def handle(self, c: Context):
        await c.send("pong")
        return
