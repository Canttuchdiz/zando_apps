import discord
from discord import app_commands
from zando.utils import PrismaExt
from zando.extentsions import UserMethods
from discord.ui import View
import traceback
import copy

class Apps(View):

    def __init__(self, instance, app_name, prisma, channel, cog):
        super().__init__(timeout=None)
        self.client = instance
        self.app_name = app_name
        self.prisma : PrismaExt = prisma
        self.channel : discord.channel.TextChannel = channel
        self.instance = cog

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        can_apply = await self.instance.can_apply(interaction, self.app_name, interaction.user.id, False)
        blacklisted = not await self.instance.can_apply(interaction, self.app_name, interaction.user.id, True)

        if not can_apply or blacklisted:

            await interaction.response.send_message("You have already applied or are blacklisted.", ephemeral=True)
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

            answers = await UserMethods.user_response(self.client, interaction.user, [question.question for question in copy.copy(questions)])

            if answers is not None:

                em = discord.Embed(color=discord.Color.blue(), title=self.app_name, description=f"User {interaction.user} ({interaction.user.id})")

                for i in range(len(answers)):
                    em.add_field(name=f"Question {i + 1}", value=answers[i])

                table = await self.instance.record_complete(interaction, self.app_name, interaction.user.id)

                await self.channel.send(embed=em)

        except Exception as e:
            traceback.print_exc()
