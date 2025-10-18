from signalbot import Command, Context, regex_triggered


class RegexTriggeredCommand(Command):
    def describe(self) -> str:
        return "😤 RegexTriggered Command: Regular Expression Decorator Example"

    @regex_triggered(r"^[\w\.-]+@gmail\.com$")
    async def handle(self, c: Context) -> None:
        await c.send("Detected a Gmail address!")
