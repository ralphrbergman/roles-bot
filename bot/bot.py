from logging import getLogger

from discord import Intents
from discord.ext.commands import (
    Bot,
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    NoEntryPointError
)

from config import TESTING_GUILD
from .db import init_db
from .utils import fmt_traceback_message, iterate_extensions

logger = getLogger('client')

class MyBot(Bot):
    def __init__(self, command_prefix: str):
        intents = Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix = command_prefix,
            help_command = None,
            intents = intents
        )

        self.test_guild = TESTING_GUILD

    async def setup_hook(self):
        await super().setup_hook()

        # Initialize database tables.
        await init_db()

        # Initiate extensions.
        for extension in iterate_extensions():
            try:
                await self.load_extension(extension)
                logger.info(f'Successfully loaded extension: {extension}')
            except ExtensionAlreadyLoaded:
                logger.error(
                    f'Extension {extension} is already loaded, skipping'
                )
            except (ExtensionFailed, NoEntryPointError) as error:
                logger.error(
                    fmt_traceback_message(
                        error,
                        f'Failed to load {extension}: check extension source.'
                    )
                )
            except ExtensionNotFound:
                logger.error(
                    f'Failed to load {extension}: '\
                    'file was potentially removed before loading.'
                )

        # Sync app commands to the testing guild.
        self.tree.copy_global_to(guild = self.test_guild)
        await self.tree.sync(guild = self.test_guild)
