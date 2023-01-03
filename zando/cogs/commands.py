from zando import *
from typing import *
from discord.ext.commands import *
from zando.utils import InvalidChannel

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





async def setup(bot):
    await bot.add_cog(Commands(bot))