from .utils import UtilMethods
from pathlib import Path
from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
import traceback
from zando.utils.config import Config
import sys
from contextlib import suppress

MY_DIR = Path(__file__).parent

load_dotenv()

TOKEN : str = os.getenv("token")

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.bans = True


class Bot(commands.Bot):

    # Initializes needed data
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    # def exception_handler(exctype, value, traceback):
    #     except AttributeError:
    #         raise InvalidTable
    #
    #     sys.__excepthook__(exctype, value, traceback)


    # Loading all cogs
    async def setup_hook(self):

        # sys.excepthook = self.exception_handler
        for filename in os.listdir(MY_DIR / "cogs"):
            if os.path.isfile(os.path.join(MY_DIR / "cogs", filename)):

                try:
                    if filename.endswith(".py"):
                        cog = f"zando.cogs.{filename[:-3]}"
                        await self.load_extension(cog)
                except Exception as e:
                    print(f"Failed to load cog {filename}")
                    traceback.print_exc()




# Creates instance of the bot and then runs it
client = Bot()

client.remove_command('help')


@client.command()
@commands.is_owner()
async def reload(ctx, cog_name):
    """Reloads a cog"""
    try:
        await client.reload_extension(f"zando.cogs.{cog_name}")
        await ctx.send(f"Reloaded cog: {cog_name}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@client.event
async def on_error(event, *args, **kwargs):
    error_tup = sys.exc_info()
    emb = discord.Embed(title=f"{event} Error", description=f"Type: {error_tup[0]}", color=discord.Color.red())
    emb.set_author(name=client.user.name, icon_url=client.user.avatar)
    emb.add_field(name="Message", value=error_tup[1])
    emb.set_footer(text=error_tup[2], icon_url=client.user.avatar)
    echannel = client.get_channel(Config.ECHANNEL)
    await echannel.send(embed=emb)

client.run(TOKEN)