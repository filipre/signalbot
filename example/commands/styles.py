from signalbot import Command, Context, triggered


class StylesCommand(Command):
    @triggered("Styles")
    async def handle(self, c: Context) -> None:
        await c.send("**Bold style**", text_mode="styled")
        await c.send("*Italic style*", text_mode="styled")
        await c.send("~Strikethrough style~", text_mode="styled")
        await c.send("||Spoiler style||", text_mode="styled")
        await c.send("`Monospaced style`", text_mode="styled")
