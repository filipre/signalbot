import logging
import os

try:
    import typer
except ImportError as exc:
    error_msg = "The 'typer' library is required to run this example."
    error_msg += " Please install it with 'pip install typer'."
    raise ImportError(error_msg) from exc

from signalbot import SignalBot, enable_console_logging


async def send(bot: SignalBot, receiver: str, text: str) -> None:
    # Wait until the bot is fully initialized before sending a message
    await bot.init_task

    await bot.send(receiver=receiver, text=text)


def main(
    receiver: str = os.environ["PHONE_NUMBER"],
    text: str = "Hello from SignalBot!",
) -> None:
    enable_console_logging(logging.INFO)

    config = {
        "signal_service": os.environ["SIGNAL_SERVICE"],
        "phone_number": os.environ["PHONE_NUMBER"],
    }
    bot = SignalBot(config)

    bot.scheduler.add_job(send, args=[bot, receiver, text])
    bot.scheduler.add_job(
        send, args=[bot, receiver, "Ping"], trigger="interval", seconds=5
    )
    bot.start()


if __name__ == "__main__":
    typer.run(main)
