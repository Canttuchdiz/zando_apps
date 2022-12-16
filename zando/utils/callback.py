
import discord
from discord.ext import commands
import pathlib

class UserReceiver():

    def __init__(self, bot : commands.Bot, data) -> None:
        self.data = data # (UTILS_DIR / "tools/jsons/quest_ans.json")
        self.answers = []
        self.client = bot


    async def user_response(self, user : discord.Member, app_name : str) -> list:

        """
        Is the kinda callback used for getting application data.
        :param user:
        :return:
        """

        # Initializes some variables
        length = len(self.data) - 1

        # Gets messages for application
        for i in range(length):

            em = discord.Embed(color=discord.Color.red())
            em.add_field(name=f"Question {i + 1}", value=self.data[i])
            em.set_footer(text="Type cancel to cancel application.")
            await user.send(embed=em)

            msg = await self.client.wait_for('message',
                                             check=lambda m: m.author == user and m.channel == user.dm_channel)
            self.answers.append(msg.content.lower())
            if "cancel" in self.answers:
                await user.send("Application successfully closed!")
                return

        fem = discord.Embed(color=discord.Color.green())
        fem.add_field(name="Congratulations!", value=self.data[length])

        lowered_response = self.answers[len(self.answers) - 1]
        if lowered_response != "submit":
            await user.send("Closed! C ya :wave:")
            return
        self.connection.add_user(str(user.id), user.name, self.table_name)
        await user.send(embed=fem)
        return self.answers
