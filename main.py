from logging import getLogger, INFO

from bot import MyBot
from config import DISCORD_TOKEN, PREFIX
from logger import f_hdlr, s_hdlr

def main() -> None:
    # Setup custom logging.
    logger = getLogger()
    logger.addHandler(f_hdlr)
    logger.addHandler(s_hdlr)
    logger.setLevel(INFO)

    # Setup bot and run it.
    bot = MyBot(command_prefix = PREFIX)
    bot.run(DISCORD_TOKEN, log_handler = None)

if __name__ == '__main__':
    main()
