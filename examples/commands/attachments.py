import base64
from pathlib import Path

from examples.commands.help import CommandWithHelpMessage
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
