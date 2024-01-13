import os
from signalbot import SignalBot, Command, Context


class StylesCommand(Command):
    async def handle(self, c: Context):
        if c.message.text == "Styles":
            await c.send("**Bold style**", text_mode="styled")
            await c.send("*Italic style*", text_mode="styled")
            await c.send("~Strikethrough style~", text_mode="styled")
            await c.send("||Spoiler style||", text_mode="styled")
            await c.send("`Monospaced style`", text_mode="styled")


if __name__ == "__main__":
    bot = SignalBot(
        {
            "signal_service": os.environ["SIGNAL_SERVICE"],
            "phone_number": os.environ["PHONE_NUMBER"],
        }
    )
    bot.register(StylesCommand())  # all contacts and groups
    bot.start()
