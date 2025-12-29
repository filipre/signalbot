from commands.help import CommandWithHelpMessage
from signalbot import Context, regex_triggered


class RegexTriggeredCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "^[\\w\\.-]+@gmail\\.com$: 😤 Regular expression decorator example."

    @regex_triggered(r"^[\w\.-]+@gmail\.com$")
    async def handle(self, c: Context) -> None:
        await c.send("Detected a Gmail address!")
