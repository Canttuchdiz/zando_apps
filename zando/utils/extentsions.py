import aiofiles
import json
import prisma
import traceback
import enum


class PrismaExt(prisma.Prisma):


    async def where_first(self, column : str, item : str) -> object:

        try:
            data = await self.application.find_first(

                where={
                    column: item
                },

            )

            return data

        except Exception as e:
            traceback.print_exc()

    async def where_unique(self, column: str, item: str) -> object:

        try:
            data = await self.application.find_unique(

                where={
                    column: item
                },

            )

            return data

        except Exception as e:
            traceback.print_exc()

    async def where_many(self, column: str, item: str) -> object:

        try:
            data = await self.application.find_many(

                where={
                    column: item
                },

            )

            return data

        except Exception as e:
            traceback.print_exc()

    async def db_data(self, obj_name : str) -> list:
        try:
            obj = getattr(self, obj_name)

            items = await obj.find_many()

            return items

        except Exception as e:
            traceback.print_exc()

    async def sql_executer(self, query : str) -> list:
        try:
            val = await self.query_raw(query)

            return val
        except Exception as e:
            traceback.print_exc()