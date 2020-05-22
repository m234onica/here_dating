import asyncio
import aiomysql

from config import Config

loop = asyncio.get_event_loop()


async def pool():

    conn = await aiomysql.connect(host=Config.HOST, port=Config.PORT, user=Config.USER, password=Config.PASSWORD, db=Config.NAME, loop=loop)


loop.run_until_complete(pool())
