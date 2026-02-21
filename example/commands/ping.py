from example.commands.help import CommandWithHelpMessage
from signalbot import Context, triggered


class PingCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "ping: 🏓 Listen for a ping and send a pong reply."

    @triggered("ping")
    async def handle(self, c: Context) -> None:
        await c.send("pong")
