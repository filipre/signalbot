import asyncio
from datetime import datetime
from pathlib import Path

from commands.help import CommandWithHelpMessage
from signalbot import Context, MessageType, triggered


class DeleteCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "delete: 🗑️ Delete a message."

    @triggered("delete")
    async def handle(self, c: Context) -> None:
        timestamp = await c.send("This message will be deleted in two seconds.")
        await asyncio.sleep(2)
        await c.remote_delete(timestamp=timestamp)


class DeleteLocalAttachmentCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "delete_attachment: 🗑️ Delete the local copy of an attachment."

    @triggered("delete_attachment")
    async def handle(self, c: Context) -> None:
        local_filenames = c.message.attachments_local_filenames
        if local_filenames is None or len(local_filenames) == 0:
            await c.send("Please send an attachment to delete.")

        for attachment_filename in local_filenames:
            attachment_path: Path = (
                Path.home()
                / ".local/share/signal-api/attachments"
                / attachment_filename
            )

            if attachment_path.exists():
                print(f"Received file {attachment_path}")  # noqa: T201

            await c.bot.delete_attachment(attachment_filename)

            if not attachment_path.exists():
                print(f"Deleted file {attachment_path}")  # noqa: T201


class ReceiveDeleteCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "N/A: 🗑️ Receive a message has been deleted notification."

    async def handle(self, c: Context) -> None:
        if c.message.type == MessageType.DELETE_MESSAGE:
            deleted_at = datetime.fromtimestamp(  # noqa: DTZ006
                c.message.remote_delete_timestamp / 1000
            )
            await c.send(f"You've deleted a message, which was sent at {deleted_at}.")
