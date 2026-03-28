import base64

from anyio import Path

from examples.commands.help import CommandWithHelpMessage
from signalbot import Context, triggered


class AttachmentCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "friday: 🦀 Send and delete an image."

    @triggered("friday")
    async def handle(self, context: Context) -> None:
        image_path = Path(__file__).parent / "image.jpeg"
        async with await image_path.open(mode="rb") as f:
            image = str(base64.b64encode(await f.read()), encoding="utf-8")

        await context.send(
            "https://www.youtube.com/watch?v=pU2SdH1HBuk",
            base64_attachments=[image],
        )
