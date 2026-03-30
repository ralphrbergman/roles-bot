from logging import getLogger

from discord import Guild
from discord.ext.commands import Bot, Cog

from bot import RolesBot
from bot.api import create_guild, delete_guild, get_guild
from bot.db import get_session

logger = getLogger('guild_handler')

class GuildHandler(Cog):
    def __init__(self, bot: RolesBot):
        self.bot = bot

    async def init_guilds(self) -> None:
        await self.bot.wait_until_ready()

        async for session in get_session():
            for guild in self.bot.guilds:
                instance = await get_guild(guild.id, session)

                if instance:
                    continue

                instance = await create_guild(guild.id, session)

    async def cog_load(self):
        self.bot.loop.create_task(self.init_guilds())

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        async for session in get_session():
            instance = await get_guild(guild.id, session)

            if instance:
                logger.info(f'Guild {guild.id} already exists in database.') 
                return

            instance = await create_guild(guild.id, session)

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        async for session in get_session():
            instance = await get_guild(guild.id, session)

            if not instance:
                logger.warning(
                    f'Guild {guild.id} doesn\'t exist in database when it '\
                    'should.'
                )
                return

            await delete_guild(instance, session)

async def setup(bot: Bot):
    await bot.add_cog(GuildHandler(bot))
