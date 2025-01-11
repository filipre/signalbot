from signalbot import Command, Context, regex_triggered


class TriggeredCommand(Command):
    def describe(self) -> str:
        return "Regex 😤 Decorator example, matches sha1 OR md5 checksums"

    # add case_sensitive=True for case sensitive triggers
    @regex_triggered(r"^[a-f0-9]{40}$", r"^[a-f0-9]{32}$")
    async def handle(self, c: Context):
        await c.send("I am triggered by regular expressions")
