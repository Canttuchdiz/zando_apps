from src import *
from src.utils import UtilMethods, UTILS_DIR
from src.utils.tools import EasySqlite

class Interactions(commands.Cog):

    """Handles interaction based commands like buttons."""

    def __init__(self, bot):
        self.client = bot
        self.table_name = "blacklist"
        self.connection = EasySqlite("data")
        self.connection.create_table(self.table_name, "ID", "Username")

    # Not necessarily a callback, but handles posting questions, and receiving user input data from dms
    # Then data is returned
    async def user_callback(self, user: discord.Member):

        """
        Is the kinda callback used for getting application data.
        :param user:
        :return:
        """
        # Initializes some variables
        data = UtilMethods.json_retriever(UTILS_DIR / "tools/jsons/quest_ans.json")
        answers = []
        length = len(data) - 1

        # Gets messages for application
        for i in range(length):

            em = discord.Embed(color=discord.Color.red())
            em.add_field(name=f"Question {i + 1}", value=data[i])
            em.set_footer(text="Type cancel to cancel application.")
            await user.send(embed=em)

            msg = await self.client.wait_for('message', check=lambda m: m.author == user and m.channel == user.dm_channel)
            answers.append(msg.content.lower())
            if "cancel" in answers:
                await user.send("Application successfully closed!")
                return

        fem = discord.Embed(color=discord.Color.green())
        fem.add_field(name="Congratulations!", value=data[length])

        lowered_response = answers[len(answers) - 1]
        if lowered_response != "submit":
            await user.send("Closed! C ya :wave:")
            return
        self.connection.add_user(str(user.id), user.name, self.table_name)
        await user.send(embed=fem)
        return answers

    @commands.check(UtilMethods.is_user)
    @commands.hybrid_command(name='blacklist', with_app_command=True)
    async def blacklist(self, ctx, user : discord.Member):

        """
        Blacklists the mentioned user.
        :param ctx:
        :param user:
        :return:
        """

        value = self.connection.user_check(str(user.id), self.table_name)

        if not value:
            self.connection.add_user(str(user.id), user.name, self.table_name)
            await ctx.send(f"{user.name} was blacklisted")
            return
        await ctx.send(f"{user.name} is already blacklisted.")




    # Calls the view containg the button.
    @commands.check_any(commands.check(UtilMethods.is_user), commands.has_role("Senior Staff Team"), commands.is_owner())
    @commands.command(aliases=['button', 'apps'])
    async def menu(self, ctx):
        """
        Sends button, which is pressed for mod apps.
        :param ctx:
        :return:
        """
        view = Menu(self)
        await ctx.send(view=view)
# The class containing the button.
class Menu(View):

    # Initializes important attributes
    def __init__(self, instance):
        super().__init__(timeout=None)
        self.value = None
        self.instance = instance

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        value = self.instance.connection.user_check(str(interaction.user.id), "blacklist")
        print(value)
        if value:
            await interaction.response.send_message("You have already applied or are blacklisted.", ephemeral=True)
        return not value

    # Creates the button, and takes data from user_callback to send to channel in embed format
    # Takes in instance of cog class to retrieve certain data
    @discord.ui.button(label="Staff Application", style=discord.ButtonStyle.red)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        client = interaction.client
        await interaction.response.send_message("Application sent to your dms :)", ephemeral=True)
        channel = client.get_channel(int(self.answer_channel))
        answer_data = await self.instance.user_callback(interaction.user)
        try:
            em = discord.Embed(color=discord.Color.blue(), title="Mod Apps", description=f"User {interaction.user} ({interaction.user.id})")
            for i in range(len(answer_data)):
                em.add_field(name=f"Question {i}", value=answer_data[i])
            await channel.send(embed=em)
        except Exception as e:
            pass

async def setup(bot):
    await bot.add_cog(Interactions(bot))