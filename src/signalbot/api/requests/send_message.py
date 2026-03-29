from signalbot.api.generated.api import SendMessageV2


class SendMessage(SendMessageV2):
    base64_attachments: list[str] | None = None
