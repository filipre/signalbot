import unittest
import asyncio
import logging
from signalbot import Command, Context


class SchnickSchnackSchnuckCommand(Command):
    triggers = ["schnick", "schnack"]

    def __init__(self, listen):
        self.listen = listen

    async def handle(self, c: Context) -> bool:
        if not Command.triggered(c.message, self.triggers):
            return

        text = c.message.text
        if text == "schnick":
            await asyncio.sleep(1)
            await c.send("schnack", listen=self.listen)
            return

        if text == "schnack":
            await asyncio.sleep(1)
            await c.send("schnuck")
            return


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    unittest.main()
