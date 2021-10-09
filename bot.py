import os

from commands import (
    TimeCommand,
    HelpCommand,
)
from signal_bot import SignalBot

if __name__ == "__main__":
    # First, link your device by generating a QR code, see https://github.com/bbernhard/signal-cli-rest-api 
    # It should create a signal-cli-config folder in the root directory (next to bot.py)
    
    # Initialize the bot
    signal_service = os.environ["SIGNAL_SERVICE"]
    phone_number = "+49123456789"
    config = {}
    bot = SignalBot(signal_service, phone_number, config)

    # Add groups to listen for. Currently, only groups are supported
    bot.listen("group", "group.group_secret")

    # Register your commands
    bot.register(TimeCommand())
    bot.register(HelpCommand())

    # Start the bot to receive and send messages
    bot.info("Bot started")
    bot.start()