import ssl
import certifi
import asyncio
import aiomysql
import aiohttp
from urllib.parse import urljoin

from config import mysql, Config
from src import message


async def pair(conn):
    user_list = []
    async with conn.cursor() as cur:
        try:
            pool = ''' SELECT
                            placeId,
                            GROUP_CONCAT(userId ORDER BY rand() SEPARATOR ",") as userId
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
                    pair = '''INSERT INTO pair(placeId, playerA, playerB) values ({}, {}, {})'''
                    placeId = group[i][0]
                    playerA = user[id]
                    playerB = user[id+1]

                    user_list.append(playerA)
                    user_list.append(playerB)

                    await cur.execute(pair.format(placeId, playerA, playerB))

                    pool = ''' UPDATE pool set deletedAt=CURRENT_TIME(), status=1 WHERE userId={} and deletedAt is NULL;'''
                    await cur.execute(pool.format(user[id]))
                    await cur.execute(pool.format(user[id+1]))
                    result = await cur.fetchall()
            await conn.commit()

        except BaseException as err:
            await conn.rollback()
            raise err

    conn.close()
    return user_list


async def pool(loop):
    conn = await aiomysql.connect(host=mysql["host"], port=3306, user=mysql["username"], password=mysql["password"], db=mysql["database"], loop=loop)
    user_list = await pair(conn)
    sslcontext = ssl.create_default_context(cafile=certifi.where())

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=sslcontext)) as session:
        tasks = []
        for userId in user_list:
            task = asyncio.create_task(message.customer_menu(session, userId))
            tasks.append(task)
        return await asyncio.gather(*tasks)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(pool(loop))
    loop.run_until_complete(future)
