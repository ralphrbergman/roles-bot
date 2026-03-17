import importlib

from discord import Forbidden, HTTPException
from discord.ext.commands import Bot, Cog, Context, command, is_owner

import bot.utils as utils
importlib.reload(utils)

import bot
import bot.exceptions as exceptions

modules = (bot, exceptions,)

for mod in modules:
    utils.recursive_reload(mod)

class ManageCommands(Cog):
    def __init__(self, bot: bot.MyBot):
        self.bot = bot

    @command()
    @is_owner()
    async def sync(
        self,
        ctx: Context,
        to_guild: bool = True
    ):
        """
        Syncs slash commands.
        Optionally you can pass a truthy value to only sync to current guild.

        Example: !sync
        Example: !sync true
        """
        guild = ctx.guild if to_guild else None

        if guild:
            message = f'Synced commands to {guild.name}'
        else:
            message = 'Globally synced commands\n'\
            'This might take an hour though'

        if guild:
            self.bot.tree.copy_global_to(guild = guild)

        try:
            await self.bot.tree.sync(guild = guild)
        except Forbidden as exception:
            raise exceptions.MissingRequiredScope('application.commands') from exception
        except HTTPException as exception:
            raise exceptions.FailedSync(getattr(guild, 'id')) from exception

        try:
            await ctx.send(message)
        except Forbidden as exception:
            raise exceptions.CantMessaeg(ctx.channel) from exception

    @command()
    @is_owner()
    async def desync(self, ctx: Context):
        """
        Clears all slash commands.
        Warning: This is destructive and can't be undone unless you reload
        the given extensions of slash commands.

        Example: !desync
        """
        self.bot.tree.clear_commands(guild = ctx.guild)
        self.bot.tree.clear_commands(guild = None)

        try:
            await ctx.send('Successfully cleared all commands.')
        except Forbidden as exception:
            raise exceptions.CantMessage(ctx.channel) from exception

        try:
            await self.bot.tree.sync()
            await self.bot.tree.sync(guild = ctx.guild)
        except Forbidden as exception:
            raise exceptions.MissingRequiredScope('application.commands') from exception
        except HTTPException as exception:
            raise exceptions.FailedSync(ctx.guild) from exception

async def setup(bot: Bot):
    await bot.add_cog(ManageCommands(bot))
