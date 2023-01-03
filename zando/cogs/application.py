import discord
from discord.ext import commands
from discord import app_commands
import pathlib
import asyncio
from prisma import Prisma
from prisma.errors import UniqueViolationError
from zando.utils import UserMethods, PrismaExt, TableTypes, InvalidChannel
import traceback
from typing import Optional
from discord.ui import View
import copy


class Application(commands.Cog):

    group = app_commands.Group(name="list", description="Groups together list commands")
    set_group = app_commands.Group(name="set", description="Sets characteristics for applications")

    def __init__(self, bot) -> None:
        self.client = bot
        self.data = None
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.connect_client())
        self.NoneType : type = type(None)

        # self.receiver = UserReceiver(self.client, self.data)

    async def connect_client(self):
        self.prisma = PrismaExt()
        await self.prisma.connect()

    async def embedify(self, title : str, message : str, color : discord.Color) -> discord.Embed:
        try:
            emb = discord.Embed(color=color)
            emb.add_field(name=title, value=message)
            return emb
        except Exception as e:
            traceback.print_exc()

    # @commands.command(name="start")
    # async def start(self, interaction, app_name : str) -> None:
    #     # Pass in list of questions
    #     self.receiver.user_response(interaction.author, )

    @app_commands.command(name="create", description="Creates a new application with specified optional requirements")
    async def create(self, interaction: discord.Interaction, app_name: str, role: str) -> None:

        try:

            table = await self.prisma.application.create(
                data={
                    'roleid': int(role),
                    'userid': interaction.user.id,
                    'application': app_name,
                    'guildId': interaction.guild_id

                }
            )
            emb = await self.embedify("Success", "Application successfully appended!", discord.Color.green())
            await interaction.response.send_message(embed=emb)

        except Exception as e:

            if not isinstance(e, UniqueViolationError):
                traceback.print_exc()
            else:
                emb = await self.embedify("Error", f"There exists an application with the name {app_name}", discord.Color.red())
                await interaction.response.send_message(embed=emb)


    # @app_commands.command(name="delete", description="Deletes specific question as indicated by input given")
    # async def delete(self, ctx, table: str):
    #     pass


    @set_group.command(name="questions", description="Sets main questions for application")
    async def set_questions(self, interaction: discord.Interaction, app_name: str, *, question1 : str, question2 : Optional[str], question3 : Optional[str], question4 : Optional[str], question5 : Optional[str], question6 : Optional[str], question7 : Optional[str], question8 : Optional[str], question9 : Optional[str], question10 : Optional[str], question11 : Optional[str], question12 : Optional[str], question13 : Optional[str], question14 : Optional[str], question15 : Optional[str]):
        try:

            namespace = interaction.namespace
            questions = [getattr(namespace, v) for v in dir(namespace) if v.startswith("question")]

            table = TableTypes.options[0]
            #
            # id = await self.prisma.where_first(table, table, app_name)

            id = await self.prisma.application.find_first(

                where={
                    table : app_name,
                    "guildId" : interaction.guild_id
                },

            )

            for question in questions:
                table = await self.prisma.question.create(
                    data={
                        'question': question,
                        'applicationId': id.id

                    }
                )
            emb = await self.embedify("Success", f"Questions successfully appended into {app_name}", discord.Color.green())
            await interaction.response.send_message(embed=emb)

        except Exception as e:

            if not isinstance(e, AttributeError):
                traceback.print_exc()
            else:
                emb = await self.embedify("Error", "Please input a valid application", discord.Color.red())
                await interaction.response.send_message(embed=emb)
            # raise InvalidTable() from None

    # @set_group.command(name="last", description="Sets last question for an application")
    # async def set_last(self, interaction : discord.Interaction):
    #     pass

    @app_commands.command(name="run", description="Runs application with specified application name and answer channel")
    async def run(self, interaction: discord.Interaction, app_name: str, answer_channel_id : str):
        try:

            channel = self.client.get_channel(int(answer_channel_id))

            if isinstance(channel, self.NoneType):
                raise InvalidChannel

            view = Apps(self.client, app_name, self.prisma, channel)
            await interaction.response.send_message(view=view)

        except Exception as e:

            if isinstance(e, AttributeError):
                emb = await self.embedify("Error", "Please input a valid application", discord.Color.red())
                await interaction.response.send_message(embed=emb)
            elif isinstance(e, InvalidChannel):
                emb = await self.embedify("Error", "Please input a valid channel id", discord.Color.red())
                await interaction.response.send_message(embed=emb)
            else:
                traceback.print_exc()

    @group.command(name="questions", description="Used for listing all questions of an application relative to guild")
    async def questions(self, interaction : discord.Interaction, app_name : str):

        try:

            items = await self.prisma.relate(app_name, *TableTypes.options, interaction.guild_id)

            element = TableTypes.options[1]

            emb = discord.Embed(color=discord.Color.blue(), title=f"{element.capitalize()} List")

            for index, row in enumerate(items):
                item = getattr(row, element)
                emb.add_field(name=f"{element.capitalize()} {index + 1}", value=item)

            await interaction.response.send_message(embed=emb)

        except Exception as e:

            if not isinstance(e, AttributeError):
                traceback.print_exc()
            else:
                emb = await self.embedify("Error", "Please input a valid application", discord.Color.red())
                await interaction.response.send_message(embed=emb)

    @group.command(name="applications", description="Used for listing all applications of specific guild")
    async def applications(self, interaction : discord.Interaction):

        try:
            element = TableTypes.options[0]

            items = await self.prisma.where_many(element, "guildId", interaction.guild_id)

            emb = discord.Embed(color=discord.Color.blue(), title=f"{element.capitalize()} List")

            for index, row in enumerate(items):
                item = getattr(row, element)
                emb.add_field(name=f"{element.capitalize()} {index + 1}", value=item)

            await interaction.response.send_message(embed=emb)

        except Exception as e:

            traceback.print_exc()


class Apps(View):

    def __init__(self, instance, app_name, prisma, channel):
        super().__init__(timeout=None)
        self.client = instance
        self.app_name = app_name
        self.prisma = prisma
        self.channel : discord.channel.TextChannel = channel


    @discord.ui.button(label="Application", style=discord.ButtonStyle.red)
    async def button(self, interaction : discord.Interaction, button : discord.ui.Button):
        try:
            await interaction.response.send_message("Application was sent in your direct messages", ephemeral=True)
            id = await self.prisma.application.find_first(
                where={
                    'application' : self.app_name,
                    'guildId' : interaction.guild_id
                }
            )

            questions = await self.prisma.where_many('question', 'applicationId', id.id)

            answers = await UserMethods.user_response(self.client, interaction.user, [question.question for question in copy.copy(questions)])

            em = discord.Embed(color=discord.Color.blue(), title=self.app_name, description=f"User {interaction.user} ({interaction.user.id})")

            for i in range(len(answers)):
                em.add_field(name=f"Question {i}", value=answers[i])

            await self.channel.send(embed=em)

        except Exception as e:
            if not isinstance(e, AttributeError):
                traceback.print_exc()
            else:
                emb = await self.embedify("Error", "Please input a valid channel id", discord.Color.red())
                await interaction.response.send_message(embed=emb)


async def setup(bot):
    await bot.add_cog(Application(bot))