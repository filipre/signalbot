from abc import abstractmethod

from signalbot import Command, Context, triggered


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
        command: CommandWithHelpMessage
        for command, _, _, _ in self.bot.commands:
            help_message += f"\t - {command.help_message()}\n"
        await context.send(help_message)
