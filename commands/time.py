from datetime import datetime

from signal_bot import Message, Command


class TimeCommand(Command):
    triggers = ["time", "🕰", "⏰"]

    def description(self) -> str:
        return "⏰, Time: Show current time"

    async def handle(self, message: Message) -> bool:
        if not Command.triggered(message, TimeCommand.triggers):
            return

        current_time = datetime.now().strftime("%H:%M:%S")
        response = f"⏰ {current_time}"
        await self.bot.send(message.group, response)
