import discord
from discord import ui, Embed
from discord.ui import Modal
from zando.utils import TableTypes, InvalidFields
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
            emb = self.instance.instance.embedify("Error", "One field must not be blank", discord.Color.red())
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







