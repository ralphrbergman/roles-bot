from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler

from discord.utils import _ColourFormatter

date_fmt = '%Y-%m-%d %H:%M:%S'
logging_fmt = '[{asctime}] [{levelname:<8}] {name}: {message}'

f_fmt = Formatter(
    logging_fmt,
    datefmt = date_fmt,
    style = '{'
)

s_fmt = _ColourFormatter(
    logging_fmt,
    datefmt = date_fmt,
    style = '{'
)

f_hdlr = RotatingFileHandler(
    'app.log',
    backupCount = 5,
    encoding = 'utf-8',
    maxBytes = 30 * 1024 * 1024
)
f_hdlr.setFormatter(f_fmt)

s_hdlr = StreamHandler()
s_hdlr.setFormatter(s_fmt)
