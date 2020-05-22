import asyncio
import aiomysql

from config import Config
from src.tool import reply
loop = asyncio.get_event_loop()


async def push_message(user):
    for userId in user:
        reply.paired(userId)


async def pair(conn):
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

        for i in range(len(group)):

            user = group[i][1].split(",")
            length = len(user)

            if length % 2 != 0:
                length -= 1

            for id in range(0, length, 2):
                pair = '''INSERT INTO pair(placeId, playerA, playerB, startedAt) values ({}, {}, {}, current_time())'''
                placeId = group[i][0]
                playerA = user[id]
                playerB = user[id+1]

                await cur.execute(pair.format(placeId, playerA, playerB))
                await conn.commit()

                pool = ''' UPDATE pool set deletedAt=CURRENT_TIME(), status=1 WHERE userId={} and deletedAt is NULL;'''
                await cur.execute(pool.format(user[id]))
                await cur.execute(pool.format(user[id+1]))
                result = await cur.fetchall()

        await conn.commit()

    conn.close()
    await push_message(user[:length])

async def pool(loop):
    conn = await aiomysql.connect(host=Config.HOST, port=Config.PORT, user=Config.USER, password=Config.PASSWORD, db=Config.NAME, loop=loop)
    await pair(conn)


loop.run_until_complete(pool(loop))
