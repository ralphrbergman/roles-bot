from logging import getLogger

from discord import Interaction
from discord.app_commands import (
    AppCommandError,
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

from bot.exceptions import CantMessage, FailedSync, MissingRequiredScope
from bot.utils import fmt_traceback_message

logger = getLogger('error_handler')

def can_react(ctx: Context) -> bool:
    permissions = ctx.bot_permissions
    return permissions.add_reactions and permissions.read_message_history

class ErrorHandler(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: CommandError):
        # Ignore commands with their own error handlers.
        if hasattr(ctx.command, 'on_error') and\
        not getattr(error, 'ignore_local_handler', False):
            return

        async def send_message(message: str) -> None:
            logger.error(message)
            await ctx.send(f'**ERROR**: {message}')

        if isinstance(error, CommandInvokeError):
            error = error.original

        if isinstance(error, CantMessage):
            logger.error(
                f'Cannot message in channel: {error.channel.name}'
            )

            if can_react(ctx):
                await ctx.message.add_reaction('🤫')
            else:
                logger.error('Can\'t react to messages in same channel.')

            return

        if isinstance(error, FailedSync):
            return await send_message(
                'Unexpected error happened syncing commands. Sync them later.'
            )

        if isinstance(error, CommandLimitReached):
            return await send_message(
                'There are way too many commands to push to a guild.'
            )

        if isinstance(error, CommandSyncFailure):
            return await send_message(
                'Ensure all synced commands have finished source.'
            )

        message = 'Unhandled exception occured during command execution:'
        logger.error(
            fmt_traceback_message(error, message)
        )

    async def on_app_command_error(
        self,
        interaction: Interaction,
        error: AppCommandError
    ):
        if hasattr(interaction.command, 'on_error') and\
        not getattr(error, 'ignore_local_handler', False):
            return

        async def send_message(message: str) -> None:
            await interaction.response.send_message(
                f'**ERROR**: {message}',
                ephemeral = True
            )

        if isinstance(error, AppCommandInvokeError):
            error = error.original

        if isinstance(error, MissingRequiredScope):
            return await send_message(
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
            await send_message('Ran into an error translating this command.')

        message = 'Unhandled exception occured during slash command execution:'
        logger.error(fmt_traceback_message(error, message))

async def setup(bot: Bot):
    await bot.add_cog(ErrorHandler(bot))
