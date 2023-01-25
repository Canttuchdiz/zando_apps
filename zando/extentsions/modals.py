import discord
from discord import ui, Embed
from discord.ui import Modal
from zando.utils import TableTypes, InvalidFields, TypeConvert, PrismaExt, UtilMethods
from typing import List
import traceback

class QuestionAdd(Modal, title='Question Addition'):

    question = ui.TextInput(label='Question', style=discord.TextStyle.paragraph)

    def __init__(self, bot, app_name, prisma, questions : list):
        super().__init__(timeout=None)
        self.client = bot
        self.app_name = app_name
        self.prisma = prisma
        self.questions = questions


    async def on_submit(self, interaction: discord.Interaction):

        self.questions.append(self.question.value)

        await interaction.response.send_message(f'Appended :smile:, {interaction.user.name}!', ephemeral=True)

class DescriptionAdd(Modal, title="Description Configuration"):


    def __init__(self, bot, app_name, prisma, embed):
        super().__init__(timeout=None)
        self.description = ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=False)
        self.add_item(self.description)
        # self.modal_items()
        self.client = bot
        self.app_name = app_name
        self.prisma = prisma
        self.embed : Embed = embed

    # def modal_items(self):
    #     labels = ("Description", "Field Name", "Field Value")
    #
    #     for label in labels:
    #         self.add_item(ui.TextInput(label=label, style=discord.TextStyle.paragraph, required=False))

    async def on_submit(self, interaction: discord.Interaction):

        self.embed.description = self.description.value
        await interaction.response.edit_message(embed=self.embed)

class FieldAdd(Modal, title="Adding Fields"):

    def __init__(self, bot, app_name, prisma, embed, instance, select):
        super().__init__(timeout=None)
        self.name = ui.TextInput(label="Name", style=discord.TextStyle.paragraph, required=False)
        self.value = ui.TextInput(label="Value", style=discord.TextStyle.paragraph, required=False)
        self.add_item(self.name)
        self.add_item(self.value)
        self.client = bot
        self.app_name = app_name
        self.prisma = prisma
        self.embed: Embed = embed
        self.instance = instance
        self.select = select


    async def interaction_check(self, interaction: discord.Interaction):

        proceed = self.name.value or self.value.value

        if not proceed:
            emb = UtilMethods.embedify("Error", "One field must not be blank", discord.Color.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)

        return proceed


    async def on_submit(self, interaction: discord.Interaction):

        options : List[discord.SelectOption] = self.select.options

        if not options[len(options) - 1].label and not options[len(options) - 1].value:
            options.pop(len(options) - 1)
            self.select.disabled = False

        self.embed.add_field(name=self.name.value, value=self.value.value)
        self.select.append_option(discord.SelectOption(label=f"Field {len(options) + 1}", value=str(len(options))))
        await interaction.response.edit_message(embed=self.embed, view=self.instance)


class ApplyAdd(Modal, title="Response Input"):

    def __init__(self, bot, app_name, question : str, embed, answer : list, index : int):
        super().__init__(timeout=None)
        self.question = question
        self.answer_response = ui.TextInput(label=self.question, style=discord.TextStyle.paragraph, required=True)
        self.add_item(self.answer_response)
        self.client = bot
        self.app_name = app_name
        self.embed : Embed = embed
        # self.view = view
        self.answer : list = answer
        self.index = index

    async def on_submit(self, interaction: discord.Interaction):

        try:
            self.answer.clear()
            # print(self.answer_response.value)
            [self.answer.append(item) for item in self.answer_response.value.split()]
            # print(self.answer)
            field = self.embed.fields[0]
            self.embed.set_field_at(index=0, name=field.name, value=self.answer_response.value)
            await interaction.response.edit_message(embed=self.embed)

        except IndexError as e:
            self.embed.add_field(name=f"Answer", value=self.answer_response.value)
            await interaction.response.edit_message(embed=self.embed)


class EditAdd(Modal, title="Response Edit"):

    def __init__(self, question: str, embed : Embed, answers : list, index: int):
        super().__init__(timeout=None)
        self.question = question
        self.answer_response = ui.TextInput(label=self.question, style=discord.TextStyle.paragraph, required=True)
        self.add_item(self.answer_response)
        self.fem: Embed = embed
        self.answers = answers
        self.index = index

    async def on_submit(self, interaction: discord.Interaction):
        self.answers[self.index] = self.answer_response.value
        field = self.fem.fields[0]
        self.fem.set_field_at(index=self.index, name=field.name, value=self.answer_response.value)
        await interaction.response.edit_message(embed=self.fem)
