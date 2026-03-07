from examples.commands.help import CommandWithHelpMessage
from signalbot import Context, triggered


class StylesCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "styles: 🎨 Demonstrates different text styles."

    @triggered("styles")
    async def handle(self, context: Context) -> None:
        await context.send("**Bold style**", text_mode="styled")
        await context.send("*Italic style*", text_mode="styled")
        await context.send("~Strikethrough style~", text_mode="styled")
        await context.send("||Spoiler style||", text_mode="styled")
        await context.send("`Monospaced style`", text_mode="styled")
