import importlib
from logging import getLogger

from discord import Guild
from discord.ext.commands import Bot, Cog

import bot.utils as utils
importlib.reload(utils)

import bot
import bot.api as api
import bot.db as db

modules = (bot, api)

for mod in modules:
    utils.recursive_reload(mod)

logger = getLogger('guild_handler')

class GuildHandler(Cog):
    def __init__(self, bot: bot.RolesBot):
        self.bot = bot

    async def init_guilds(self) -> None:
        await self.bot.wait_until_ready()

        async for session in db.get_session():
            for guild in self.bot.guilds:
                instance = await api.get_guild(guild.id, session)

                if instance:
                    continue

                instance = await api.create_guild(guild.id, session)

    async def cog_load(self):
        self.bot.loop.create_task(self.init_guilds())

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        async for session in db.get_session():
            instance = await api.get_guild(guild.id, session)

            if instance:
                logger.info(f'Guild {guild.id} already exists in database.') 
                return

            instance = await api.create_guild(guild.id, session)

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        async for session in db.get_session():
            instance = await api.get_guild(guild.id, session)

            if not instance:
                logger.warning(
                    f'Guild {guild.id} doesn\'t exist in database when it '\
                    'should.'
                )
                return

            await api.delete_guild(instance, session)

async def setup(bot: Bot):
    await bot.add_cog(GuildHandler(bot))
