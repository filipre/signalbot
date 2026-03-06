import asyncio

from examples.commands.help import CommandWithHelpMessage
from signalbot import Context, triggered


class TypingCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "typing: ⌨️ Demonstrates typing indicator for a few seconds."

    @triggered("typing")
    async def handle(self, context: Context) -> None:
        await context.start_typing()
        seconds = 5
        await asyncio.sleep(seconds)
        await context.stop_typing()
        await context.send(f"Typed for {seconds}s")
