import importlib
from logging import getLogger

from discord import Interaction
from discord.app_commands import (
    AppCommandError,
    CheckFailure,
    CommandInvokeError as AppCommandInvokeError,
    CommandLimitReached,
    CommandSyncFailure,
    MissingApplicationID,
    TranslationError
)
from discord.ext.commands import (
    Bot,
    Cog,
    Context,
    CommandError,
    CommandInvokeError
)

import bot.utils as utils
importlib.reload(utils)

import bot.exceptions as exceptions

modules = (exceptions,)

for mod in modules:
    utils.recursive_reload(mod)

logger = getLogger('error_handler')

def can_react(ctx: Context) -> bool:
    permissions = ctx.bot_permissions
    return permissions.add_reactions and permissions.read_message_history

class ErrorHandler(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @classmethod
    async def send_message(
        cls,
        ctx: Context,
        error: CommandError,
        message: str
    ) -> None:
        log_message = 'Error happened during command execution: '\
        f'{ctx.command} | {ctx.author}: {utils.get_traceback(error)}'

        logger.error(log_message)
        await ctx.send(f'**ERROR**: {message}')

    async def send_interaction_message(
        cls,
        interaction: Interaction,
        error: AppCommandError,
        message: str
    ) -> None:
        log_message = 'Error happened during app command execution: '\
        f'{interaction.command} | {interaction.user}: '\
        f'{utils.get_traceback(error)}'

        logger.error(log_message)
        await interaction.response.send_message(
            f'**ERROR**: {message}',
            ephemeral = True
        )

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: CommandError):
        if isinstance(error, CommandInvokeError):
            error = error.original

        if getattr(error, 'ignore_local_handler', False):
            pass
        # Ignore commands with their own error handlers.
        elif hasattr(ctx.command, 'on_error'):    return

        if isinstance(error, exceptions.CantMessage):
            logger.error(
                f'Cannot message in channel: {error.channel}'
            )

            if can_react(ctx):
                await ctx.message.add_reaction('🤫')
            else:
                logger.error('Can\'t react to messages in same channel.')

            return

        if isinstance(error, exceptions.FailedSync):
            return await ErrorHandler.send_message(
                ctx,
                error,
                'Unexpected error happened syncing commands. Sync them later.'
            )

        if isinstance(error, CommandLimitReached):
            return await ErrorHandler.send_message(
                ctx,
                error,
                'There are way too many commands to push to a guild.'
            )

        if isinstance(error, CommandSyncFailure):
            return await ErrorHandler.send_message(
                ctx,
                error,
                'Ensure all synced commands have finished source.'
            )

        message = 'Unexpected error happened during command execution: '\
        f'{ctx.command} | {ctx.author}: {utils.get_traceback(error)}'

        logger.error(message)

    async def on_app_command_error(
        self,
        interaction: Interaction,
        error: AppCommandError
    ):
        if isinstance(error, (AppCommandInvokeError, CheckFailure)):
            error = error.original if hasattr(error, 'original') else error

        if hasattr(interaction.command, 'on_error') and\
        not getattr(error, 'ignore_local_handler', False):
            return

        if isinstance(error, exceptions.HasRole):
            return await ErrorHandler.send_interaction_message(
                interaction,
                error,
                'You already have a role!'
            )

        if isinstance(error, exceptions.MissingRequiredScope):
            return await ErrorHandler.send_interaction_message(
                interaction,
                error,
                f'I have a missing {error.scope} scope.'\
                'Please re-invite me with that scope enabled!'
            )

        if isinstance(error, MissingApplicationID):
            return logger.error('I don\'t have my application ID received.')

        if isinstance(error, TranslationError):
            logger.error(
                f'Translation failed for locale: {error.locale}; '\
                f'Message: {error.string}'
            )
            await ErrorHandler.send_interaction_message(
                interaction,
                error,
                'Ran into an error translating this command.'
            )

        message = 'Unexpected error happened during app command execution: '\
        f'{interaction.command} | User: {interaction.user}: '\
        f'{utils.get_traceback(error)}'

        logger.error(message)

async def setup(bot: Bot):
    await bot.add_cog(ErrorHandler(bot))
