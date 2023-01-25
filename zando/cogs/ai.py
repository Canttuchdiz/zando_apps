import discord
from discord.ext import commands
from discord import app_commands

class AICog(commands.Cog):

    def __init__(self, bot):
        self.client = bot




async def setup(bot):
    await bot.add_cog(AICog(bot))