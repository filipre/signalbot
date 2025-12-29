from commands.help import CommandWithHelpMessage
from signalbot import Context, triggered


class ReplyCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "reply: 💬 Reply to a message."

    @triggered("reply")
    async def handle(self, c: Context) -> None:
        await c.reply("This is a reply.")
