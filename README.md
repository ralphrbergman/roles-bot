# Example Bot
A modular Discord bot boilerplate built with discord.py library, designed for rapid development and easy component reuse.

## Installation
* Download repository with `git clone https://github.com/ralphrbergman/roles-bot`
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
4. Finally, run the bot with `python main.py`

## Features

## License
This repository is licensed under GPLv2 license available here: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
