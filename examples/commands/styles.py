from examples.commands.help import CommandWithHelpMessage
from signalbot import Context, triggered


class StylesCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "styles: 🎨 Demonstrates different text styles."

    @triggered("styles")
    async def handle(self, c: Context) -> None:
        await c.send("**Bold style**", text_mode="styled")
        await c.send("*Italic style*", text_mode="styled")
        await c.send("~Strikethrough style~", text_mode="styled")
        await c.send("||Spoiler style||", text_mode="styled")
        await c.send("`Monospaced style`", text_mode="styled")
