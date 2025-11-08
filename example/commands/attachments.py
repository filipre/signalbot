import asyncio
import base64
from pathlib import Path

from commands.help import CommandWithHelpMessage
from signalbot import Context, triggered


class AttachmentCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "friday: 🦀 Send and delete an image."

    @triggered("friday")
    async def handle(self, c: Context) -> None:
        with open(Path(__file__).parent / "image.jpeg", "rb") as f:  # noqa: ASYNC230, PTH123
            image = str(base64.b64encode(f.read()), encoding="utf-8")

        await c.send(
            "https://www.youtube.com/watch?v=pU2SdH1HBuk",
            base64_attachments=[image],
        )

        await asyncio.sleep(2)  # Give the user time to see the image

        for attachment_filename in c.message.attachments_local_filenames:
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
