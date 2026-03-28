from examples.commands.help import CommandWithHelpMessage
from signalbot import Context, reaction_triggered


class ReactionCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "react with any emoji: 👍 Reaction decorator example."

    @reaction_triggered()
    async def handle(self, context: Context) -> None:
        reaction = context.message.reaction
        if reaction.is_remove:
            await context.send(f"You removed your {reaction.emoji} reaction")
            return
        await context.send(
            f"{reaction.emoji} from {context.message.source} "
            f"on message at {reaction.target_sent_timestamp}"
        )


class ThumbsUpCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "react with 👍 or ❤️: 🎯 Filtered reaction decorator example."

    @reaction_triggered("👍", "❤️")
    async def handle(self, context: Context) -> None:
        await context.send("Thanks for the love!")
