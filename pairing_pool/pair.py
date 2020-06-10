import ssl
import certifi
import asyncio
import aiomysql
import aiohttp
from urllib.parse import urljoin

from config import mysql, Config
from src import message


async def insert(loop, sql, data, pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.executemany(sql, data)
            except BaseException as err:
                await conn.rollback()
                raise err
            else:
                await conn.commit()


async def pair(loop, pool):
    user_list = []
    data = []
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            get_pool_data = ''' SELECT
                            placeId,
                            GROUP_CONCAT(userId ORDER BY rand() SEPARATOR ",") as userId
                        FROM
                            pool
                        WHERE
                            deletedAt is NULL
                        GROUP BY
                            placeId; '''
            await cur.execute(get_pool_data)
            group = await cur.fetchall()

            for i in range(len(group)):

                user = group[i][1].split(",")

                length = len(user)

                if length % 2 != 0:
                    length -= 1
                for id in range(0, length, 2):
                    placeId = group[i][0]
                    playerA = user[id]
                    playerB = user[id+1]

                    user_list.append(playerA)
                    user_list.append(playerB)

                    data.append((placeId, playerA, playerB),)

    pair_sql = '''INSERT INTO pair (placeId, playerA, playerB) values (%s, %s, %s);'''
    pool_sql = '''UPDATE pool set deletedAt=CURRENT_TIME(), status=1 WHERE placeId=%s and userId=%s or userId=%s and deletedAt is NULL;'''

    tasks = [
        asyncio.create_task(
            insert(loop=loop, sql=pair_sql, data=data, pool=pool)),
        asyncio.create_task(
            insert(loop=loop, sql=pool_sql, data=data, pool=pool))
    ]

    result = await asyncio.gather(*tasks)
    return user_list


async def main(loop):
    pool = await aiomysql.create_pool(host=mysql["host"], port=3306, user=mysql["username"], password=mysql["password"], db=mysql["database"], loop=loop)
    user_list = await pair(loop, pool)
    pool.close()

    sslcontext = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=sslcontext)) as session:
        tasks = []
        for userId in user_list:
            task = asyncio.create_task(message.customer_menu(session, userId))
            tasks.append(task)
        return await asyncio.gather(*tasks)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(main(loop))
    loop.run_until_complete(future)
