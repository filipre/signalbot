from abc import abstractmethod

from signalbot import Command, Context, triggered
from signalbot.api.requests import SendMessage


class CommandWithHelpMessage(Command):
    @abstractmethod
    def help_message(self) -> str:
        pass


class HelpCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "help: 🆘 Shows information about available commands."

    @triggered("help")
    async def handle(self, context: Context) -> None:
        help_message = "Available commands:\n"
        for command, _, _, _ in self.bot.commands:
            if isinstance(command, CommandWithHelpMessage):
                help_message += f"\t - {command.help_message()}\n"
        await context.send(SendMessage(message=help_message))
