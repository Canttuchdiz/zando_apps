from zando import *
from typing import *
import discord
from discord.ext.commands import *
from discord import app_commands
from zando.utils import InvalidChannel, Config

class Commands(commands.Cog):

    """
    Arbitrary commands, ranging from little to high importance.
    """

    def __init__(self, bot):
        self.client = bot

    # Gets the instnace of the bot and registers a command which returns the latency of the command.
    @commands.command(aliases=['pingpong'])
    async def ping(self, ctx, *, question=None):
        await ctx.send('Pong! {0}'.format(round(self.client.latency, 1)))

    # Shuts down bot, which can only be used by users in id_list in utils
    @commands.check(UtilMethods.is_user)
    @commands.command(aliases=['end', 'shutoff'])
    async def close(self, ctx):
        await ctx.send("Shutting down... :wave: bye!")
        await self.client.close()

    @commands.is_owner()
    @commands.command(aliases=['guilds'])
    async def guildcount(self, ctx):
        await ctx.send(f"{len(self.client.guilds)}")

    # def exception_handler(exctype, value, traceback):
    #     if exctype == InvalidTable:
    #         pass

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @app_commands.command(name="maintenance", description="Notifies owners of servers with the bot if there is downtime")
    @app_commands.guilds(Config.MGUILD_ID)
    async def maintenance(self, interaction: discord.Interaction, start_time: str):
        await interaction.response.send_message(content=f"Sent a warning to {len(self.client.guilds)} Guild(s)")
        for guild in self.client.guilds:
            globalrestart_embed = discord.Embed(title="# ~ | ZandoApps Restart",
                                                description=f"ZandoApps will face downtime starting {start_time}.\nWe'll use this time to migrate new changes towards the bot and patch any Errors.\nFor any questions or concerns, don't be afraid to [join our support server](https://discord.gg/Z2RkeYxD6k).\nThis downtime was issued by `{interaction.user}`")
            globalrestart_embed.set_footer(text="ZandoApps™️ | Restart Occuring Soon",
                                            icon_url="https://images-ext-1.discordapp.net/external/Qx2Yrx3EPyG3e71-cVFQuwxwti3ilhVrlasdoHgcanY/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1037943321143812127/86536711183b7f56b1de9dcada217281.png") \
                , globalrestart_embed.add_field(name="Guild Being Affected:", value=f"{guild.name} ({guild.id})")
            await guild.owner.send(embed=globalrestart_embed)


async def setup(bot):
    await bot.add_cog(Commands(bot))