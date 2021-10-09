import aiohttp
import websockets


class SignalAPI:
    def __init__(
        self,
        signal_service: str,
        phone_number: str,
    ):
        self.signal_service = signal_service
        self.phone_number = phone_number

        self.session = None

    async def receive(self):
        try:
            uri = self._receive_ws_uri()
            async with websockets.connect(uri, ping_interval=None) as websocket:
                async for raw_message in websocket:
                    yield raw_message
        except Exception:
            raise ReceiveMessagesError

    async def send(self, message: str, receiver: str) -> aiohttp.ClientResponse:
        if self.session is None:
            self.session = aiohttp.ClientSession()

        # POST new message
        uri = self._send_rest_uri()
        payload = {
            "message": message,
            "number": self.phone_number,
            "recipients": [receiver],
        }
        try:
            resp = await self.session.post(uri, json=payload)
            resp.raise_for_status()
            return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise SendMessageError

    async def react(self, reaction: str, timestamp: int) -> aiohttp.ClientResponse:
        uri = self._react_rest_uri(self)
        payload = {
            "reaction": reaction,
            "timestamp": timestamp,
            # "number": "", # TODO
            # "recipient": "", # TODO
        }
        try:
            resp = await self.session.post(uri, json=payload)
            resp.raise_for_status()
            return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise SendMessageError

    def _receive_ws_uri(self):
        return f"ws://{self.signal_service}/v1/receive/{self.phone_number}"

    def _send_rest_uri(self):
        return f"http://{self.signal_service}/v2/send"

    def _react_rest_uri(self):
        return f"http://{self.signal_service}/v1/react"


class ReceiveMessagesError(Exception):
    pass


class SendMessageError(Exception):
    pass
