import ssl
import certifi
import asyncio
import aiomysql
import aiohttp
import logging
from urllib.parse import urljoin

from config import mysql, Config
from pair import message

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.WARNING)


async def insert(loop, sql, data, pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.executemany(sql, data)
            except BaseException as err:
                logging.error("SQL insert is rollback.", exc_info=True)
                await conn.rollback()
                raise err
            else:
                await conn.commit()


async def unpair_count(loop, pool):
    status = 0
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            sql = ''' select placeId, count(*) from pool where deletedAt is NULL group by placeId; '''
            await cur.execute(sql)
            counts = await cur.fetchall()
            for count in counts:
                if int(count[1]) >= 2:
                    status = 1
    return status


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
                            deletedAt is NULL AND createdAt > CURRENT_TIME() - INTERVAL {} MINUTE
                        GROUP BY
                            placeId; '''
            await cur.execute(get_pool_data.format(Config.EXPIRED_TIME))
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
    status = await unpair_count(loop, pool)
    while status != 0:
        user_list = await pair(loop, pool)
        status = await unpair_count(loop, pool)
    pool.close()
    await pool.wait_closed()

    sslcontext = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=sslcontext)) as session:
        tasks = []
        for userId in user_list:
            task = asyncio.create_task(message.customer_menu(session, userId))
            tasks.append(task)
        return await asyncio.gather(*tasks)
