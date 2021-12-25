import os
from src.signalbot import SignalBot
from example.commands import PingCommand, FridayCommand, TypingCommand


def main():
    signal_service = os.environ["SIGNAL_SERVICE"]
    phone_number = os.environ["PHONE_NUMBER"]
    group_id = os.environ["GROUP_ID"]
    group_secret = os.environ["GROUP_SECRET"]

    config = {
        "signal_service": signal_service,
        "phone_number": phone_number,
        "storage": None,
    }
    bot = SignalBot(config)

    bot.listen(group_id, group_secret)

    bot.register(PingCommand())
    bot.register(FridayCommand())
    bot.register(TypingCommand())

    bot.start()


if __name__ == "__main__":
    main()
