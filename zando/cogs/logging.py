import discord
from discord.ext import commands
from zando.utils.config import Config

class LogCog(commands.Cog):

    def __init__(self, bot):
        self.client : commands.Bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild : discord.Guild):
        try:
            invite = await guild.system_channel.create_invite()
        except AttributeError as e:
            for channel in guild.channels:
                if not isinstance(channel, discord.Thread) and not isinstance(channel, discord.CategoryChannel):
                    invite = await channel.create_invite()

        server_channel = self.client.get_channel(Config.LGCHANNEL)
        emb = discord.Embed(title=guild.name, description=invite.url, color=discord.Color.blue())
        emb.add_field(name="Member Count", value=guild.member_count)
        emb.set_author(name=guild.owner.name, icon_url=guild.owner.avatar)
        emb.set_footer(text=f"ID : {guild.id}", icon_url=self.client.user.avatar)

        await server_channel.send(embed=emb)


async def setup(bot):
    await bot.add_cog(LogCog(bot))