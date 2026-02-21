import asyncio

from example.commands.help import CommandWithHelpMessage
from signalbot import Context, triggered


class TypingCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "typing: ⌨️ Demonstrates typing indicator for a few seconds."

    @triggered("typing")
    async def handle(self, c: Context) -> None:
        await c.start_typing()
        seconds = 5
        await asyncio.sleep(seconds)
        await c.stop_typing()
        await c.send(f"Typed for {seconds}s")
