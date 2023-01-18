import discord
from discord import app_commands
from discord.ui import Modal
from discord import Embed
from .modals import QuestionAdd, DescriptionAdd, FieldAdd, PrismaExt, TypeConvert, TableTypes, UtilMethods
from .selects import Fields
from zando.utils.util import UtilMethods
from discord.ui import View
import traceback
import copy
from typing import List
import json
from prisma import Json

class Apps(View):

    def __init__(self, instance, app_name, prisma, channel, cog, role_id):
        super().__init__(timeout=None)
        self.client = instance
        self.instance = cog
        self.app_name = app_name
        self.prisma : PrismaExt = self.instance.prisma
        self.channel : discord.channel.TextChannel = channel
        self.role_id = role_id
        self.applying : List[discord.Member] = self.instance.applying

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        is_applying : bool = interaction.user.id in self.applying
        has_role : bool = True if self.role_id in [role.id for role in interaction.user.roles] else False
        can_apply : bool = await self.instance.can_apply(interaction, self.app_name, interaction.user.id, False)
        blacklisted : bool = not await self.instance.can_apply(interaction, self.app_name, interaction.user.id, True)

        if not can_apply or blacklisted:

            await interaction.response.send_message("You have already applied or are blacklisted.", ephemeral=True)
            return False

        elif is_applying:

            await interaction.response.send_message("You are in the middle of an application", ephemeral=True)
            return False

        elif not has_role:

            await interaction.response.send_message("You do not have the role necessary to take the application", ephemeral=True)
            return False

        return can_apply



    @discord.ui.button(label="Application", style=discord.ButtonStyle.red)
    async def button(self, interaction : discord.Interaction, button : discord.ui.Button):
        try:

            id = await self.prisma.application.find_first(
                where={
                    'application' : self.app_name,
                    'guildId' : interaction.guild_id
                }
            )

            questions = await self.prisma.where_many('question', 'applicationId', id.id)

            await interaction.response.send_message("Application was sent in your direct messages", ephemeral=True)

            self.applying.append(interaction.user.id)

            from .callback import UserMethods
            answers = await UserMethods.user_response(self.client, interaction.user, self.app_name, [question.question for question in copy.copy(questions)])

            self.applying.remove(interaction.user.id)

            if answers is not None:

                em = discord.Embed(color=discord.Color.blue(), title=self.app_name, description=f"User {interaction.user} ({interaction.user.id})")

                for i in range(len(answers)):
                    em.add_field(name=f"Question {i + 1}", value=answers[i])

                table = await self.instance.record_complete(interaction, self.app_name, interaction.user.id)

                await self.channel.send(embed=em)

        except Exception as e:
            traceback.print_exc()

class Create(View):

    # Get values then submit button actually publishes changes by adding to db
    def __init__(self, bot, instance, app_name, prisma, role, reapply):
        super().__init__(timeout=None)
        self.client = bot
        self.instance = instance
        self.app_name = app_name
        self.prisma = prisma
        self.questions = []
        self.role = role
        self.reapply = reapply

    @discord.ui.button(label="Add Question", style=discord.ButtonStyle.blurple)
    async def question_add(self, interaction : discord.Interaction, button : discord.ui.Button):

        try:

            modal = QuestionAdd(self.client, self.app_name, self.prisma, self.questions)

            await interaction.response.send_modal(modal)

        except Exception as e:
            traceback.print_exc()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction : discord.Interaction, button : discord.ui.Button):
        await UtilMethods.cancel_interaction("Cancellation successful", f"{self.app_name} was not created", interaction, self.instance)


    @discord.ui.button(label="Done", style=discord.ButtonStyle.green)
    async def done(self, interaction : discord.Interaction, button : discord.ui.Button):

        try:

            table = await self.prisma.application.create(
                data={
                    'roleid': int(self.role.id),
                    'userid': interaction.user.id,
                    'application': self.app_name,
                    'reapply': TypeConvert.a[self.reapply],
                    'guildId': interaction.guild_id

                }
            )

            if self.questions:

                table = TableTypes.options[0]
                #
                # id = await self.prisma.where_first(table, table, app_name)

                id = await self.prisma.application.find_first(

                    where={
                        table: self.app_name,
                        "guildId": interaction.guild_id
                    },

                )

                for question in self.questions:
                    table = await self.prisma.question.create(
                        data={
                            'question': question,
                            'applicationId': id.id

                        }
                    )

            emb = UtilMethods.embedify("Success", f"Questions successfully appended into {self.app_name}",
                                      discord.Color.green())
            await interaction.response.edit_message(embed=emb, view=None)

        except Exception as e:
            traceback.print_exc()

class QuestionEdit(View):

    def __init__(self, bot, instance, prisma, app_name):
        super().__init__(timeout=None)
        self.client = bot
        self.instance = instance
        self.prisma : PrismaExt = prisma
        self.app_name : str = app_name
        self.questions = []

    @discord.ui.button(label="Add Question", style=discord.ButtonStyle.primary)
    async def adder(self, interaction : discord.Interaction, button : discord.ui.Button):
        pass

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await UtilMethods.cancel_interaction("Question setting session was closed", interaction, self.instance)


class AppEmbed(View):

    def __init__(self, bot, instance, prisma, app_name, embed : Embed):
        super().__init__(timeout=None)
        self.options = [discord.SelectOption(label='', value='', description="")]
        self.select = Fields(self.options)
        self.add_item(self.select)
        self.client = bot
        self.instance = instance
        self.prisma : PrismaExt = prisma
        self.app_name = app_name
        self.embed = embed


    @discord.ui.button(label="Add Description", style=discord.ButtonStyle.primary)
    async def description(self, interaction: discord.Interaction, button: discord.ui.Button):

        modal = DescriptionAdd(self.client, self.app_name, self.prisma, self.embed)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Add Field", style=discord.ButtonStyle.primary)
    async def field_add(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = FieldAdd(self.client, self.app_name, self.prisma, self.embed, self, self.select)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await UtilMethods.cancel_interaction("Embed configuration session was closed", interaction, self.instance)

    @discord.ui.button(label="Done", style=discord.ButtonStyle.success)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        emb_json = self.embed.to_dict()
        await self.prisma.config.create(
            data={
                'embed' : Json(emb_json),
                'application' : self.app_name,
                'guildId' : interaction.guild_id
            }
        )

        emb = UtilMethods.embedify("Configuration Successful", "Embed successfully appended to application",
                                     discord.Color.green())
        await interaction.response.edit_message(embed=emb, view=None)



class TakeApp(View):

    def __init__(self, bot, app_name : str):
        super().__init__(timeout=None)
        self.client = bot
        self.app_name = app_name

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await UtilMethods.cancel_interaction("Application has been closed!", interaction, self.instance)

