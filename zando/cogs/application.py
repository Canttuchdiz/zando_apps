import discord
from discord.ext import commands
from discord import app_commands
import pathlib
import asyncio
from prisma import Prisma
from prisma.errors import UniqueViolationError
from zando.utils import PrismaExt, TableTypes, InvalidChannel, InvalidApp
from zando.extentsions import UserMethods, Apps
import traceback
from typing import Optional
from discord.ui import View
import copy


class Application(commands.Cog):

    group = app_commands.Group(name="list", description="Groups together list commands")
    set_group = app_commands.Group(name="set", description="Sets characteristics for applications")
    blacklist_group = app_commands.Group(name="blacklist", description="Handles blacklisting sets and deletions")

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

    async def valid_app(self, interaction : discord.Interaction, app_name : str) -> bool:

        try:
            app = await self.prisma.application.find_first(
                where={
                    "application": app_name,
                    "guildId": interaction.guild_id
                }
            )

            return bool(app)

        except Exception as e:
            traceback.print_exc()

    async def can_apply(self, interaction : discord.Interaction, app_name : str, user_id : int, blacklist : bool) -> bool:

        try:
            check = False

            value = await self.prisma.application.find_first(
                where={
                    'application': app_name,
                    'guildId': interaction.guild_id
                }
            )



            if value:
                if value.reapply:
                    check = await self.prisma.records.find_first(
                        where={
                            'userId': user_id,
                            'application': app_name,
                            'guildId': interaction.guild_id,
                            'blacklist' : blacklist
                        }
                    )

            return bool(check)

        except Exception as e:
            traceback.print_exc()

    async def record_complete(self, interaction : discord.Interaction, app_name : str, user_id : int, blacklist : Optional[bool] = False):

        try:
            table = await self.prisma.records.create(
                data={
                    'userId': user_id,
                    'application': app_name,
                    'guildId': interaction.guild_id,
                    'blacklist' : blacklist
                }
            )
            return table
        except Exception as e:
            traceback.print_exc()

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

    @app_commands.command(name="create", description="Creates a new application with the id of the lowest role allowed to start the application")
    async def create(self, interaction: discord.Interaction, app_name: str, role_id: str, can_reapply : bool) -> None:

        try:

            table = await self.prisma.application.create(
                data={
                    'roleid': int(role_id),
                    'userid': interaction.user.id,
                    'application': app_name,
                    'reapply' : can_reapply,
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
    #

    # @set_group.command(name="config", description="Is used to configure some aspects of the bot")
    # async def configuration(self, interaction : discord.Interaction, editorId : int):
    #     try:
    #         table = await self.prisma.config.create(
    #             data={
    #                 "role_id" : editorId,
    #                 "guildId" : interaction.guild_id
    #             }
    #         )
    #
    #     except Exception as e:
    #         traceback.print_exc()

    @blacklist_group.command(name="add", description="Blacklists a user from taking an application")
    async def blacklist(self, interaction : discord.Interaction, app_name : str, user_id : str):
        try:

            app = await self.valid_app(interaction, app_name)

            if not app:
                raise InvalidApp

            blacklisted = await self.can_apply(interaction, app_name, int(user_id), True)
            user : discord.Member = self.client.get_user(int(user_id))

            if blacklisted:
                await interaction.response.send_message(f"{user.name} has already applied or is blacklisted.", ephemeral=True)
                return

            table = await self.record_complete(interaction, app_name, int(user_id), True)

            await interaction.response.send_message(f"{user.name} has been blacklisted from {app_name}", ephemeral=True)

        except Exception as e:

            if isinstance(e, InvalidApp):
                emb = await self.embedify("Error", "Please provide a valid application", discord.Color.red())
                await interaction.response.send_message(embed=emb)
            elif isinstance(e, AttributeError):
                emb = await self.embedify("Error", "Please provide a valid user id", discord.Color.red())
                await interaction.response.send_message(embed=emb)
            else:
                traceback.print_exc()

    @blacklist_group.command(name="remove", description="Allows user to apply after they have applied or have been blacklisted")
    async def remove(self, interaction : discord.Interaction, app_name : str, user_id : str):
        try:

            app = await self.valid_app(interaction, app_name)

            if not app:
                raise InvalidApp

            blacklisted : bool = await self.can_apply(interaction, app_name, int(user_id), True)

            user: discord.Member = self.client.get_user(int(user_id))

            print(blacklisted)

            if blacklisted:


                await self.prisma.records.delete_many(
                    where={
                        'userId' : user_id,
                        'application' : app_name,
                        'guildId' : interaction.guild_id,
                        'blacklist' : True
                    }
                )

                await interaction.response.send_message(f"{user.name} successfully unblacklisted", ephemeral=True)
                return

            await interaction.response.send_message(f"{user.name} has not been blacklisted", ephemeral=True)

        except Exception as e:

            if isinstance(e, InvalidApp):
                emb = await self.embedify("Error", "Please provide a valid application", discord.Color.red())
                await interaction.response.send_message(embed=emb)
            elif isinstance(e, AttributeError):
                emb = await self.embedify("Error", "Please provide a valid user id", discord.Color.red())
                await interaction.response.send_message(embed=emb)
            else:
                traceback.print_exc()

    @group.command(name="blacklisted", description="Lists members who can't reapply; whether by blacklist or already applied")
    async def blacklist_List(self, interaction : discord.Interaction, app_name : str):

        try:

            app = await self.valid_app(interaction, app_name)

            if not app:
                raise InvalidApp

            records = await self.prisma.records.find_many(
                where={
                    'application' : app_name,
                    'guildId' : interaction.guild_id,
                    'blacklist' : True

                }
            )

            users = [self.client.get_user(data.userId) for data in records]

            emb = discord.Embed(title="Blacklisted/Applied Users", color=discord.Color.blurple())

            for index, user in enumerate(users):
                emb.add_field(name=f"User {index + 1}", value=f"{user.name} ({user.id})")

            await interaction.response.send_message(embed=emb)

        except Exception as e:

            if isinstance(e, InvalidApp):
                emb = await self.embedify("Error", "Please provide a valid application", discord.Color.red())
                await interaction.response.send_message(embed=emb)
            elif isinstance(e, AttributeError):
                emb = await self.embedify("Error", f"{e}", discord.Color.red())
                await interaction.response.send_message(embed=emb)
            else:
                traceback.print_exc()


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
            app = await self.valid_app(interaction, app_name)

            if isinstance(app, self.NoneType):
                raise InvalidApp
            elif isinstance(channel, self.NoneType):
                raise InvalidChannel


            view = Apps(self.client, app_name, self.prisma, channel, self)
            await interaction.response.send_message(view=view)

        except Exception as e:

            if isinstance(e, AttributeError):
                emb = await self.embedify("Error", "Please input a valid application", discord.Color.red())
                await interaction.response.send_message(embed=emb)
            elif isinstance(e, InvalidChannel):
                emb = await self.embedify("Error", "Please provide a valid channel id", discord.Color.red())
                await interaction.response.send_message(embed=emb)
            elif isinstance(e, InvalidApp):
                emb = await self.embedify("Error", "Please provide a valid application", discord.Color.red())
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


async def setup(bot):
    await bot.add_cog(Application(bot))