import discord
from discord import Interaction
from discord.app_commands import AppCommandError
from discord.ext import commands
from zando.utils.config import Config
from zando.utils import InvalidApp, InvalidEmbed, UtilMethods
import traceback
import sys

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
            emb = UtilMethods.embedify("Error", str(error), discord.Color.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)

        elif isinstance(error, InvalidEmbed):
            emb = UtilMethods.embedify(str(error), "Please create an embed for your application with /application embed", discord.Color.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)

        else:
            emb = discord.Embed(title="Error", description=f"Type: {type(error)}", color=discord.Color.red())
            emb.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
            emb.add_field(name="Message", value=error)
            emb.set_footer(text=error.__traceback__, icon_url=self.bot.user.avatar)
            echannel = self.bot.get_channel(1065009230215647323)
            await echannel.send(embed=emb)
            # traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

async def setup(bot):
    await bot.add_cog(Handlers(bot))