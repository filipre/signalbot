import base64
from pathlib import Path
from signalbot import Command, Context


class AttachmentCommand(Command):
    def describe(self) -> str:
        return "🦀 Congratulations sailor, you made it to friday!"

    async def handle(self, c: Context):
        if c.message.text == "friday":
            with open(Path(__file__).parent / "image.jpeg", "rb") as f:
                image = str(base64.b64encode(f.read()), encoding="utf-8")

            await c.send(
                "https://www.youtube.com/watch?v=pU2SdH1HBuk",
                base64_attachments=[image],
            )
            return
