from collections.abc import Callable, Mapping
from logging import getLogger
from typing import Any, Optional

from discord import ButtonStyle, Embed, Forbidden, HTTPException, Interaction
from discord.ext.commands import (
    Bot,
    Cog,
    Command,
    Context,
    CommandError,
    Group,
    HelpCommand,
)
from discord.ui import Button, View, button

from bot.exceptions import CantMessage
from bot.utils import fmt_traceback_message

logger = getLogger('help_command')

# How many commands to show per page.
PAGINATION_SIZE = 5

async def handle_pagination(
    filter_commands: Callable,
    command_prefix: str,
    commands: list[Command],
    setup_embed: Callable[..., Embed],
    **kwargs: Any
) -> list[Embed]:
    filtered = await filter_commands(
        commands,
        sort = True
    )
    chunks = [
        filtered[index : index + PAGINATION_SIZE]
        for index in range(0, len(filtered), PAGINATION_SIZE)
    ]

    # Build list of embeds.
    pages = []

    for index, chunk in enumerate(chunks):
        page_number = index + 1
        page = setup_embed(
            **kwargs,
            page_number = page_number,
            chunks = len(chunks)
        )

        for cmd in chunk:
            page.add_field(
                name = cmd.name,
                value = cmd.help or cmd.short_doc or 'No info',
                inline = False
            )

        page.set_footer(
            text = f'{len(filtered)} commands available, check more at '\
            f'{command_prefix}help <command-name>'
        )

        pages.append(page)

    # Provide an empty pages page.
    if not pages:
        page = setup_embed(
            **kwargs,
            page_number = 0,
            chunks = len(chunks)
        )
        page.description = 'There are no pages for your input.'

        pages.append(page)

    return pages

class HelpPaginator(View):
    def __init__(self, pages: list[Embed]):
        super().__init__(timeout = 60)

        self.current_page = 0
        self.pages = pages
        self.total_pages = len(pages)

        self.update_buttons()

    async def on_timeout(self):
        await super().on_timeout()

        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
                item.style = ButtonStyle.gray

        if hasattr(self, 'message'):
            try:
                await self.message.edit(view = self)
            except HTTPException as exception:
                pass

    def update_buttons(self) -> None:
        self.previous_btn.disabled = self.current_page == 0
        self.next_btn.disabled = self.current_page == self.total_pages - 1

    async def update_view(self, interaction: Interaction) -> None:
        self.update_buttons()

        await interaction.response.edit_message(
            embed = self.pages[self.current_page],
            view = self
        )

    @button(label = 'Previous', style = ButtonStyle.blurple)
    async def previous_btn(self, interaction: Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_view(interaction)

    @button(label = 'Next', style = ButtonStyle.blurple)
    async def next_btn(self, interaction: Interaction, button: Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await self.update_view(interaction)

class PrettierHelpCommand(HelpCommand):
    async def on_help_command_error(self, ctx: Context, error: CommandError):
        await super().on_help_command_error(ctx, error)

        logger.error(
            fmt_traceback_message(
                error,
                'Unexpected error occured during display of help page:'
            )
        )

    async def send_bot_help(
        self,
        mapping: Mapping[Optional[Cog], list[Command]]
    ):
        """
        Invoked when basically !help is called.
        """
        # Flatten mapping of commands.
        cmds = [ cmd for commands in mapping.values() for cmd in commands ]

        def setup_embed(**kwargs) -> Embed:
            e = Embed(
                title = f'Help - Page {kwargs.get('page_number')}/'\
                f'{kwargs.get('chunks')}'
            )
            return e

        pages = await handle_pagination(
            self.filter_commands,
            self.context.prefix,
            cmds,
            setup_embed
        )

        channel = self.get_destination()
        view = HelpPaginator(pages)

        try:
            message = await channel.send(embed = pages[0], view = view)
        except Forbidden as exception:
            raise CantMessage(channel.id) from exception

        view.message = message

    async def send_cog_help(self, cog: Cog):
        """
        Invoked when !help <cog-name> is called.
        """
        def setup_embed(**kwargs) -> Embed:
            e = Embed(
                title = f'{getattr(kwargs.get('cog'), 'qualified_name')} '\
                'Category',
                description = getattr(
                    kwargs.get('cog'), 'help', 'No info'
                )
            )

            return e

        pages = await handle_pagination(
            self.filter_commands,
            self.context.prefix,
            cog.get_commands(),
            setup_embed,
            cog = cog
        )

        channel = self.get_destination()
        view = HelpPaginator(pages)

        try:
            await channel.send(embed = pages[0], view = view)
        except Forbidden as exception:
            raise CantMessage(channel.id) from exception

    async def send_command_help(self, command: Command):
        e = Embed(
            title = f'Command "{command.qualified_name}"'
        )

        e.add_field(
            name = 'Description',
            value = command.help or 'No info',
            inline = False
        )

        e.add_field(
            name = 'Cooldown',
            value = command.cooldown,
            inline = False
        )

        e.add_field(
            name = 'Usage',
            value = f'`{self.get_command_signature(command)}`',
            inline = False
        )

        channel = self.get_destination()

        try:
            await channel.send(embed = e)
        except Forbidden as exception:
            raise CantMessage(channel.id) from exception

    async def send_group_help(self, group: Group):
        """
        Invoked when !help <group-name> is called.
        """
        def setup_embed(**kwargs) -> Embed:
            e = Embed(
                title = f'{getattr(kwargs.get('group'), 'qualified_name')} '\
                'Command Group',
                description = getattr(
                    kwargs.get('group'), 'help', 'No info'
                )
            )

            return e

        pages = await handle_pagination(
            self.filter_commands,
            self.context.prefix,
            group.commands,
            setup_embed,
            group = group
        )

        channel = self.get_destination()
        view = HelpPaginator(pages)

        try:
            await channel.send(embed = pages[0], view = view)
        except Forbidden as exception:
            raise CantMessage(channel.id) from exception

class HelpCommandCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        bot.help_command = PrettierHelpCommand()

async def setup(bot: Bot):
    await bot.add_cog(HelpCommandCog(bot))
