
import discord
from discord.ext import commands
from .views import TakeApp, Apps, Create, AppConfigMenu, AppEmbed, SubmitApp, ImportView
from datetime import datetime
import pathlib

class UserMethods:

    def __init__(self, bot : commands.Bot, data) -> None:
        self.data = data # (UTILS_DIR / "tools/jsons/quest_ans.json")
        self.answers = []
        self.client = bot


    #Make more efficent later
    @staticmethod
    async def user_response(client : commands.Bot, user : discord.Member, app_name : str, questions : list, coro) -> list:

        """
        Is the kinda callback used for getting application data.
        :param user:
        :return:
        """


        # Initializes some variables
        answers = []
        view = TakeApp(client, app_name)
        # questF = [quest for quest in questions if "last" in quest][0]

        # Gets messages for application
        for i, question in enumerate(questions):

            # Creates new embed for each question in db
            em = discord.Embed(title=app_name, description="Placeholder: *Application used for playing games!*",
                               color=discord.Color.purple())
            em.add_field(name=f"Question {i + 1}", value=question)
            em.set_footer(text=f"{user.id} · " + datetime.now().strftime(r"%I:%M %p"), icon_url=user.avatar)
            await user.send(embed=em, view=view)

            # Waits for user response
            msg : discord.Message = await client.wait_for('message',
                                             check=lambda m: m.author == user and m.channel == user.dm_channel)
            # Checks if cancel is a response
            answers.append(msg.content)
            await msg.add_reaction('✅')
            #
            # for answer in answers:
            #     if answer.lower() == "cancel":
            #         await user.send("Application successfully closed!")
            #         return
            
        view = SubmitApp(client, app_name, answers)
        await user.send(view=view)
        await view.wait()
        return answers
