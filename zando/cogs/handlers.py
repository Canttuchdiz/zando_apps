import discord
from discord import Interaction
from discord.app_commands import AppCommandError
from discord.ext import commands
from zando.utils import InvalidApp, InvalidEmbed
from zando.cogs.application import Application

class Handlers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -> Option 1 ---
    # attaching the handler when the cog is loaded
    # this is required for option 1
    def cog_load(self):
        tree = self.bot.tree
        self.bot._old_tree_error = tree.on_error
        tree.on_error = self.on_app_command_error

    # -> Option 1 ---
    # detaching the handler when the cog is unloaded
    # this is optional for option 1
    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self.bot._old_tree_error

    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):

        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, InvalidApp):
            emb = Application.embedify("Error", str(error), discord.Color.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)

        elif isinstance(error, InvalidEmbed):
            emb = Application.embedify(str(error), "Please create an embed for your application with /application embed", discord.Color.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Handlers(bot))