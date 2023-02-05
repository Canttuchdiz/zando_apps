from zando import *
from discord import app_commands
from discord.ext import commands
import discord
from zando.utils import Config
from discord.errors import Forbidden
from typing import Optional

"""This custom help command is a perfect replacement for the default one on any Discord Bot written in Discord.py!
However, you must put "bot.remove_command('help')" in your bot, and the command must be in a cog for it to work.
Original concept by Jared Newsom (AKA Jared M.F.)
[Deleted] https://gist.github.com/StudioMFTechnologies/ad41bfd32b2379ccffe90b0e34128b8b
Rewritten and optimized by github.com/nonchris
https://gist.github.com/nonchris/1c7060a14a9d94e7929aa2ef14c41bc2
You need to set three variables to make that cog run.
Have a look at line 51 to 57
"""


async def send_embed(ctx, embed):
    """
    Function that handles the sending of embeds
    -> Takes context and embed to send
    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)


class Help(commands.Cog):
    """
    Sends this help message
    """

    def __init__(self, bot):
        self.client: commands.Bot = bot

    @app_commands.command(name='help', description='Lists all available commands')
    async def help(self, interaction : discord.Interaction):
        emb = discord.Embed(title="Help", description='Zando Apps is a feature rich and customizable questionnaire and application bot to help enhance your community!',
                            color=discord.Color.blue())
        slash_cmds = [f"``/{command.name}``" for command in self.client.tree.get_commands()]
        cmds = '**|**'.join(slash_cmds)
        emb.add_field(name="Commands", value=cmds)
        emb.set_author(name=self.client.user.name, icon_url=self.client.user.avatar)
        emb.set_footer(text=f"ID : {interaction.user.id}", icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=emb)


async def setup(bot):
    await bot.add_cog(Help(bot))