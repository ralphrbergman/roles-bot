import importlib
from logging import getLogger

from discord import Forbidden
from discord.ext.commands import (
    Bot,
    Cog,
    Context,
    CommandError,
    CommandInvokeError,
    ExtensionAlreadyLoaded,
    ExtensionError,
    ExtensionFailed,
    ExtensionNotFound,
    ExtensionNotLoaded,
    NoEntryPointError,
    command,
    is_owner
)

import bot.utils as utils
importlib.reload(utils)

import bot
import bot.exceptions as exceptions

modules = (bot, exceptions,)

for mod in modules:
    utils.recursive_reload(mod)

logger = getLogger('manage_extensions')

class ManageExtensions(Cog):
    def __init__(self, bot: bot.MyBot):
        self.bot = bot

    @classmethod
    async def send_error_message(cls, ctx: Context, message: str) -> None:
        logger.error(message)
        await ctx.send(f'**ERROR**: {message}')

    @command()
    @is_owner()
    async def list_extensions(self, ctx: Context):
        """
        Lists every loaded extension.
        """
        try:
            await ctx.send(
                ', '.join(f'`{extension.split('.')[-1]}`'
                for extension in self.bot.extensions.keys())
            )
        except Forbidden as exception:
            raise exceptions.CantMessage(ctx.channel) from exception

    @command()
    @is_owner()
    async def load(self, ctx: Context, name: str):
        """
        Loads given extension.
        Example: !load manage_extensions
        """
        extension = utils.get_partial_name(name)

        if not extension:
            raise ExtensionNotFound(name)

        await self.bot.load_extension(extension)

        try:
            await ctx.send(
                f'Successfully loaded extension: `{extension}`'
            )
        except Forbidden as exception:
            raise exceptions.CantMessage(ctx.channel) from exception

    @load.error
    async def load_error(self, ctx: Context, error: CommandError):
        if isinstance(error, CommandInvokeError):
            error = error.original

        name = getattr(error, 'name', 'Unknown')

        if isinstance(error, ExtensionAlreadyLoaded):
            return await ManageExtensions.send_error_message(
                ctx,
                'Extension is already loaded.'
            )
        elif isinstance(error, (ExtensionFailed, NoEntryPointError)):
            message = 'Extension source isn\'t complete.'
            message = utils.fmt_traceback_message(error, message)
            return await ManageExtensions.send_error_message(ctx, message)
        elif isinstance(error, ExtensionNotFound):
            return await ManageExtensions.send_error_message(
                ctx,
                f'Extension: `{name}`: can\'t be found.'
            )

        error.ignore_local_handler = True
        await self.bot.on_command_error(ctx, error)

    @command()
    @is_owner()
    async def reload(self, ctx: Context, name: str):
        """
        Reloads given extension.
        Example: !reload manage_extensions
        """
        extension = utils.get_partial_name(name)

        if not extension:
            raise ExtensionNotFound(name)

        await self.bot.reload_extension(extension)

        try:
            await ctx.send(f'Extension: `{extension}`: successfully reloaded')
        except Forbidden as exception:
            raise exceptions.CantMessage(ctx.channel) from exception

    @reload.error
    async def reload_error(self, ctx: Context, error: CommandError):
        if isinstance(error, CommandInvokeError):
            error = error.original

        name = getattr(error, 'name', 'Unknown')

        if isinstance(error, (ExtensionFailed, NoEntryPointError)):
            message = f'Failed to reload: `{name}`: check extension source.'
            message = utils.fmt_traceback_message(error, message)

            return await ManageExtensions.send_error_message(ctx, message)
        elif isinstance(error, ExtensionNotFound):
            return await ManageExtensions.send_error_message(
                ctx,
                f'Extension: `{name}`: can\'t be found.'
            )
        elif isinstance(error, ExtensionNotLoaded):
            return await ManageExtensions.send_error_message(
                ctx,
                f'Extension: `{name}`: isn\'t loaded.'
            )

        error.ignore_local_handler = True
        await self.bot.on_command_error(ctx, error)

    @command()
    @is_owner()
    async def reload_all(self, ctx: Context):
        """
        Reloads all loaded (active) extensions.
        """
        extensions = list(self.bot.extensions.keys())

        # Set of failed and successful extension reloads respectfully.
        failed, completed = set(), set()

        for extension in extensions:
            try:
                await self.bot.reload_extension(extension)

                completed.add(extension)
            except ExtensionError as error:
                message = utils.fmt_traceback_message(error, 'Reload all command failed:')
                logger.error(message)

                failed.add(extension)

        message = f'Reloaded extensions: {
            ', '.join(f'`{extension.split('.')[-1]}`'
            for extension in completed)
        }'

        if len(failed):
            message += f'\nFailed extensions: {
                ', '.join(f'`{extension.split('.')[-1]}`'
                for extension in failed)
            }'

        try:
            await ctx.send(message)
        except Forbidden as exception:
            raise exceptions.CantMessage(ctx.channel) from exception

    @command()
    @is_owner()
    async def unload(self, ctx: Context, name: str):
        """
        Unloads given extension.
        Example: !unload manage_extensions
        """
        extension = utils.get_partial_name(name)

        if not extension:
            raise ExtensionNotFound(name)

        await self.bot.unload_extension(extension)

        try:
            await ctx.send(
                f'Extension: `{name}`: successfully unloaded'
            )
        except Forbidden as exception:
            raise exceptions.CantMessage(ctx.channel) from exception

    @unload.error
    async def unload_error(self, ctx: Context, error: CommandError):
        if isinstance(error, CommandInvokeError):
            error = error.original

        name = getattr(error, 'name', 'Unknown')

        if isinstance(error, ExtensionNotFound):
            return await ManageExtensions.send_error_message(
                ctx,
                f'Extension: `{name}`: can\'t be found.'
            )
        elif isinstance(error, ExtensionNotLoaded):
            return await ManageExtensions.send_error_message(
                ctx,
                f'Extension: `{name}`: isn\'t loaded.'
            )

        error.ignore_local_handler = True
        await self.bot.on_command_error(ctx, error)

async def setup(bot: Bot):
    await bot.add_cog(ManageExtensions(bot))
