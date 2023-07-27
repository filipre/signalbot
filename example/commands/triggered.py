from signalbot import Command, Context, triggered


class TriggeredCommand(Command):
    def describe(self) -> str:
        return "😤 Decorator example, matches command_1, command_2 and command_3"

    # add case_sensitive=True for case sensitive triggers
    @triggered("command_1", "Command_2", "CoMmAnD_3")
    async def handle(self, c: Context):
        await c.send("I am triggered")
