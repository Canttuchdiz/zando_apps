import discord
from discord.ext import commands
from discord import app_commands
import pathlib
import asyncio
from prisma import Prisma
from zando.utils import UserReceiver, PrismaExt, TableTypes
import traceback

class Application(commands.Cog):

    def __init__(self, bot) -> None:
        self.client = bot
        self.data = None
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.connect_client())
        # self.receiver = UserReceiver(self.client, self.data)

    async def connect_client(self):
        self.prisma = PrismaExt()
        await self.prisma.connect()

    # @commands.command(name="start")
    # async def start(self, interaction, app_name : str) -> None:
    #     # Pass in list of questions
    #     self.receiver.user_response(interaction.author, )

    @commands.command(name="create")
    async def create(self, ctx, app_name : str, role : int) -> None:

        try:
            table = await self.prisma.application.create(
                data={
                    'roleid' : int(role),
                    'userid' : ctx.author.id,
                    'application' : app_name

                }
            )

            await ctx.send("Application successfully appended!")
        except Exception as e:
            # await ctx.send("You provided invalid or incomplete arguments")
            traceback.print_exc()


    @commands.command(name="delete")
    async def delete(self, ctx):
        pass


    @commands.command(name="set")
    async def set(self, ctx, app_name : str, *, questions_list : str):
        try:

            id = await self.prisma.where_first('application', app_name)

            questions = questions_list.strip('][').split(', ')

            for question in questions:
                table = await self.prisma.question.create(
                    data={
                        'question': question,
                        'applicationId': id.id

                    }
                )

        except Exception as e:

            print(traceback.print_exc())


    @commands.command(name="list")
    async def list(self, ctx, param : str):
        try:

            element = TableTypes.options[int(param)]

            items = await self.prisma.db_data(element)
            print(type(items))

            emb = discord.Embed(color=discord.Color.blue(), title=f"{element.capitalize()} List")

            for index, row in enumerate(items):
                item = getattr(row, element)
                emb.add_field(name=f"{element.capitalize()} {index + 1}", value=item)

            await ctx.send(embed=emb)

        except Exception as e:
            traceback.print_exc()

        #     emb = discord.Embed(color = discord.Color.blue(), title=f"{TableTypes.types[int(type)]} List")
        #
        #     for index, app in enumerate(items):
        #
        #         emb.add_field(name=f'App{index + 1}', value=app.name)
        #     await ctx.send(embed=emb)
        #
        # except Exception as e:
        #
        #     await ctx.send(traceback.format_exc())


async def setup(bot):
    await bot.add_cog(Application(bot))