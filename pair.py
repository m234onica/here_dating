import asyncio
import aiomysql

from config import Config
from src.tool import reply
loop = asyncio.get_event_loop()


async def pool():

    conn = await aiomysql.connect(host=Config.HOST, port=Config.PORT, user=Config.USER, password=Config.PASSWORD, db=Config.NAME, loop=loop)

    async with conn.cursor() as cur:

        pool = ''' SELECT 
                        placeId, 
                        GROUP_CONCAT(userId SEPARATOR ",") as userId
                    FROM
                        pool 
                    WHERE 
                        deletedAt is NULL 
                    GROUP BY 
                        placeId; '''
        await cur.execute(pool)
        group = await cur.fetchall()

    conn.close()

loop.run_until_complete(pool())
