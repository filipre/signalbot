from signalbot import Command, Context, regex_triggered


class RegexTriggeredCommand(Command):
    def describe(self) -> str:
        return "😤 RegexTriggered Command: Regular Expression Decorator Example"

    @regex_triggered(r"^[a-f0-9]{40}$", r"^[a-f0-9]{32}$")
    async def handle(self, c: Context):
        await c.send("I am triggered by regular expressions")
