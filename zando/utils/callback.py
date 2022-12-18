
import discord
from discord.ext import commands
import pathlib

class UserMethods:

    def __init__(self, bot : commands.Bot, data) -> None:
        self.data = data # (UTILS_DIR / "tools/jsons/quest_ans.json")
        self.answers = []
        self.client = bot


    #Make more efficent later
    @staticmethod
    async def user_response(client : commands.Bot, user : discord.Member, questions : list) -> list:

        """
        Is the kinda callback used for getting application data.
        :param user:
        :return:
        """

        # Initializes some variables
        length = len(questions) - 1
        answers = []

        # Gets messages for application
        for i in range(length):

            em = discord.Embed(color=discord.Color.red())
            em.add_field(name=f"Question {i + 1}", value=questions[i])
            em.set_footer(text="Type cancel to cancel application.")
            await user.send(embed=em)

            msg = await client.wait_for('message',
                                             check=lambda m: m.author == user and m.channel == user.dm_channel)
            answers.append(msg.content.lower())
            if "cancel" in answers:
                await user.send("Application successfully closed!")
                return

        fem = discord.Embed(color=discord.Color.green())
        fem.add_field(name="Congratulations!", value=questions[length])

        lowered_response = answers[len(answers) - 1]
        if lowered_response != "submit":
            await user.send("Closed! C ya :wave:")
            return
        await user.send(embed=fem)
        return answers
