from typing import Optional

from discord import Guild, TextChannel
from discord.app_commands import AppCommandError

class BaseExc(AppCommandError):
    ignore_local_handler = True

class CantMessage(BaseExc):
    """
    Exception raised when the bot can't message channel
    a command was invoked in.
    """
    def __init__(self, channel: TextChannel):
        self.channel = channel

class FailedSync(BaseExc):
    """ Exception raised when syncing commands to a guild fails. """
    def __init__(self, guild: Optional[Guild]):
        self.guild = guild

class MissingRequiredScope(BaseExc):
    """
    Exception raised when the bot doesn't have given scope
    """
    def __init__(self, scope: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scope = scope
