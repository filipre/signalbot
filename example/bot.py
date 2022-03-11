import os
from signalbot import SignalBot
from commands import PingCommand, FridayCommand, TypingCommand, TriggeredCommand
import logging

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.WARNING)


def main():
    signal_service = os.environ["SIGNAL_SERVICE"]
    phone_number = os.environ["PHONE_NUMBER"]
    group_id = os.environ["GROUP_ID"]
    internal_id = os.environ["GROUP_INTERNAL_ID"]

    config = {
        "signal_service": signal_service,
        "phone_number": phone_number,
        "storage": None,
    }
    bot = SignalBot(config)

    bot.listen(group_id, internal_id)

    bot.register(PingCommand())
    bot.register(FridayCommand())
    bot.register(TypingCommand())
    bot.register(TriggeredCommand())

    bot.start()


if __name__ == "__main__":
    main()
