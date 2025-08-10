import unittest
import asyncio
import logging
from signalbot import Command, Context, triggered


class SchnickSchnackSchnuckCommand(Command):
    def __init__(self):
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


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    unittest.main()
