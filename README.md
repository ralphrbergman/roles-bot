# Example Bot
A modular Discord bot boilerplate built with discord.py library, designed for rapid development and easy component reuse.

## Installation
* Download repository with `git clone https://github.com/ralphrbergman/example-bot`
* Make sure you have Python installed, at least Python 3.12 to be exact
* Run `python -m venv venv` to create a new Python Virtual Environment
* and enter the environment<br>
Linux/macOS: `source venv/bin/activate`<br>
Windows: `venv\Scripts\activate`
* and finally run `pip install -r requirements.txt` to install all dependencies needed to host the bot.
* Make sure that your Discord bot has the Messages intent enabled on Discord developer portal, this is necessary to load/unload extensions on the fly.
* Rename `.env.example` to `.env` and paste in your Discord bot token after the string `DISCORD_TOKEN=`
* Provide your testing Discord server ID after `TESTING_GUILD=`

## Usage
1. Create an extension (bot/extensions/my_extension.py):
```py
from discord.ext.commands import Bot, Cog

from bot import MyBot

class MyCog(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot

async def setup(bot: Bot):
    await bot.add_cog(MyCog())
```

2. Create a command (bot/extensions/ping.py):
```py
from discord import Interaction
from discord.app_commands import command
from discord.ext.commands import Bot, Cog

from bot import MyBot

class MyCog(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot

    @command()
    async def ping(self, interaction: Interaction):
    await interaction.response.send_message(f'Pong (in `{round(self.bot.latency)}` ms)')

async def setup(bot: Bot):
    await bot.add_cog(MyCog(bot))
```

3. Define a database table (bot/db/models/role.py).
```py
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel

class Role(BaseModel):
    __tablename__ = 'role'
    role_id: Mapped[int] = mapped_column(nullable = False, unique = True)
    user_id: Mapped[int] = mapped_column(nullable = False)
```

4. Finally, run the bot with `python main.py`

## Features
* Logging into a log file
* Easy database integration with SQLAlchemy
* Support for dynamic discord.py extensions
* Error handling
* Prefix help command
* Extension management

## License
This repository is licensed under GPLv2 license available here: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
