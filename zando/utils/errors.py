import sys
from discord.app_commands import AppCommandError

class InvalidChannel(Exception):
    pass

class InvalidApp(AppCommandError):
    """Raised when invalid app is passed in"""
    pass

class InvalidFields(Exception):
    pass

class InvalidEmbed(AppCommandError):
    """Raised for any embed error"""
    pass
