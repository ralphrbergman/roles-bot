from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from discord import Object

load_dotenv()

DISCORD_TOKEN = getenv('DISCORD_TOKEN')
EXTENSIONS_PATH = Path(getenv('EXTENSIONS_PATH', 'bot/extensions'))
PREFIX = getenv('PREFIX', '!')
SKIP_RELOAD = ('bot.db', 'bot.db.database',)
TESTING_GUILD = Object(id = getenv('TESTING_GUILD'))
