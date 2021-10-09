from signal_bot import Message, Command


class HelpCommand(Command):
    triggers = ["signalbot", "🤖", "help", "commands"]

    def description(self) -> str:
        return "🤖, Signalbot: Show all commands"

    async def handle(self, message: Message) -> str:
        if not Command.triggered(message, HelpCommand.triggers):
            return

        response = ["🤖 Signalbot\n"]
        if len(self.bot.active_commands) == 0:
            response.append("No active commands")
        for command in self.bot.active_commands:
            desc = command.description()
            if desc is None:
                continue
            response.append(f"• {command.description()}")

        await self.bot.reply(message, "\n".join(response))
