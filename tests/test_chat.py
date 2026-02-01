import asyncio

from signalbot import Command, Context, triggered


class SchnickSchnackSchnuckCommand(Command):
    def __init__(self):  # noqa: ANN204
        pass

    @triggered("schnick", "schnack")
    async def handle(self, c: Context) -> bool:
        text = c.message.text
        if text == "schnick":
            await asyncio.sleep(1)
            await c.send("schnack")
            return

        if text == "schnack":
            await asyncio.sleep(1)
            await c.send("schnuck")
            return
