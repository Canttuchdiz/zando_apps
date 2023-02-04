from discord.ext import commands
from zando import *
from zando.utils import UtilMethods, UTILS_DIR, InvalidChannel, Config


class Events(commands.Cog):
    """
    Handles events, and encapsulates two event commands.
    """


    def __init__(self, bot):
        self.client : commands.Bot = bot
        # self.id_list = UtilMethods.json_retriever(UTILS_DIR / 'tools/jsons/id_data.json')

    # Sets up do not disturb and it's "Listening to Cube"
    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready!')
        print('Logged in as ---->', self.client.user)
        print('ID:', self.client.user.id)
        print(f'Version: {Config.VERSION}')
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Zando Apps"), status=discord.Status.do_not_disturb)

    #Excepts errors, handles them accordingly, and sends new exceptions to stderr for the interpreter to print out.

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):

        if message.channel.id == Config.ECHANNEL:

            # id of error channel in testing server
            etchannel = self.client.get_channel(1071538644994760895)
            emb = message.embeds[0]
            await etchannel.send(embed=emb)

        if self.client.user.mentioned_in(message) and await self.client.is_owner(message.author):
            await message.reply("Hey hottie :kiss: :heart:")




    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        ignored = (commands.CommandNotFound,)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        # elif isinstance(error, InvalidTable):
        #     await ctx.send("Please provide a valid table")

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.NotOwner):
            await ctx.send(f"{ctx.command} is reserved for the bot owners.")

            # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
                await ctx.send('I could not find that member. Please try again.')

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            # print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            # traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            emb = discord.Embed(title="Invoke Handler", description=f"Type: {type(error)}", color=discord.Color.red())
            emb.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
            emb.add_field(name="Message", value=error)
            emb.set_footer(text=error.__traceback__, icon_url=self.client.user.avatar)
            echannel = self.client.get_channel(Config.ECHANNEL)
            await echannel.send(embed=emb)

        """Below is an example of a Local Error Handler for our command do_repeat"""


async def setup(bot):
    await bot.add_cog(Events(bot))