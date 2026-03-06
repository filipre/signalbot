from examples.commands.help import CommandWithHelpMessage
from signalbot import Context, triggered


class TriggeredCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "command_1, command_2 or command_3: 😤😤😤 Decorator example."

    # add case_sensitive=True for case sensitive triggers
    @triggered("command_1", "Command_2", "CoMmAnD_3")
    async def handle(self, context: Context) -> None:
        await context.send("I am triggered")
