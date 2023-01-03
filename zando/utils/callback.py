
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
        questions.append("Do you want to submit? To submit write **submit** or **cancel** to cancel")
        answers = []
        # questF = [quest for quest in questions if "last" in quest][0]

        # Gets messages for application
        for i, question in enumerate(questions):

            # Creates new embed for each question in db
            em = discord.Embed(color=discord.Color.red())
            em.add_field(name=f"Question {i + 1}", value=question)
            em.set_footer(text="Type cancel to cancel application.")
            await user.send(embed=em)

            # Waits for user response
            msg = await client.wait_for('message',
                                             check=lambda m: m.author == user and m.channel == user.dm_channel)
            # Checks if cancel is a response
            answers.append(msg.content)
            if "cancel" == [answer.lower() for answer in answers]:
                await user.send("Application successfully closed!")
                return


        fem = discord.Embed(title="Application successfully submitted!", color=discord.Color.green())

        # Writes final response congratulating using question_last

        final_response = answers[len(answers) - 1].lower()
        if final_response != "submit":
            await user.send("Closed! C ya :wave:")
            return
        await user.send(embed=fem)
        return answers[:-1]
