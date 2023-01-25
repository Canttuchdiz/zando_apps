import aiofiles
import json
import discord
import prisma
import traceback
import enum
from typing import Literal

class UtilMethods:

    # Contains methods that I will use to reduce redundancy

    @staticmethod
    def is_user(ctx) -> bool:
        id_list = [520741459478052886, 841851864429625404]
        return ctx.author.id in id_list

    @staticmethod
    def json_retriever(path: str):
        with open(path, encoding='utf-8') as f:
            content = f.read()
            return json.loads(content)

    @staticmethod
    async def cancel_interaction(view, body : str, interaction : discord.Interaction):
        emb = UtilMethods.embedify("Cancellation successful", body,
                                     discord.Color.red())
        await interaction.response.edit_message(embed=emb, view=None)
        view.stop()


    @staticmethod
    def embedify(title : str, message : str, color : discord.Color) -> discord.Embed:
        emb = discord.Embed(color=color)
        emb.add_field(name=title, value=message)
        return emb



class TableTypes:

    options: list = ['application', 'question']

class TypeConvert:

    a = {"Yes" : True, "No" : False}

