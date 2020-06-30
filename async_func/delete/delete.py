import ssl
import certifi
import asyncio
import aiomysql
import aiohttp
import logging
from datetime import datetime

from config import mysql, Config
from delete import message

logging.basicConfig(
    format='%(asctime)s %(levelname)s - %(message)s', level=logging.INFO)

async def update(loop, sql, data, pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.executemany(sql, data)
            except BaseException as err:
                logging.error("SQL update is rollback.", exc_info=True)
                await conn.rollback()
                raise err
            else:
                await conn.commit()


async def select_pool(loop, pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            sql = '''SELECT id, placeId, userId
                    FROM pool
                    WHERE deletedAt IS NULL AND createdAt <= CURRENT_TIME() - INTERVAL {} MINUTE;'''

            await cur.execute(sql.format(Config.EXPIRED_TIME))
            return await cur.fetchall()


async def select_pair(loop, pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            pair_expired_sql = ''' 
                        SELECT id, playerA
                        FROM pair
                        WHERE deletedAt IS NULL AND createdAt <= CURRENT_TIME() - INTERVAL 3 MINUTE
                        UNION ALL
                        SELECT id, playerB
                        FROM pair
                        WHERE deletedAt IS NULL AND createdAt <= CURRENT_TIME() - INTERVAL 3 MINUTE;'''
            await cur.execute(pair_expired_sql.format(Config.END_TIME, Config.END_TIME))
            pair_list = await cur.fetchall()
            return [list(row) for row in pair_list]


async def delete(loop, pool):
    # For update sql
    pool_id = []
    pair_id = []
    # For messenger
    pool_list = []
    pair_list = []

    pool_data = await select_pool(loop, pool)
    for data in pool_data:
        pool_id.append(data[0])
        pool_list.append(data[1:])

    pair_list = await select_pair(loop, pool)
    for data in pair_list:
        pair_id.append(data[0])
    pair_id = list(set(pair_id))

    delete_pool_sql = '''UPDATE pool SET deletedAt=CURRENT_TIME() WHERE id=%s AND deletedAt IS NULL;'''
    delete_pair_sql = '''UPDATE pair SET deletedAt=CURRENT_TIME(), status='end' WHERE id=%s AND deletedAt IS NULL;'''

    tasks = [
        asyncio.create_task(
            update(loop=loop, sql=delete_pool_sql, data=pool_id, pool=pool)),
        asyncio.create_task(
            update(loop=loop, sql=delete_pair_sql, data=pair_id, pool=pool))
    ]
    await asyncio.gather(*tasks)
    return pool_list, pair_list


async def main(loop):
    start_time = datetime.now()
    pool_list = []
    pair_list = []

    pool = await aiomysql.create_pool(host=mysql["host"], port=3306, user=mysql["username"], password=mysql["password"], db=mysql["database"], loop=loop)
    pool_list, pair_list = await delete(loop, pool)
    pool.close()
    await pool.wait_closed()

    sslcontext = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=sslcontext)) as session:
        pool_tasks = []
        pair_tasks = []

        for data in pool_list:
            task = asyncio.create_task(
                message.delet_pool_menu(session, data[0], data[1]))
            pool_tasks.append(task)

        for data in pair_list:
            task = asyncio.create_task(
                message.delet_pair_menu(session, data[0], data[1]))
            pair_tasks.append(task)
        await asyncio.gather(*pool_tasks, *pair_tasks)
        end_time = datetime.now()
        logging.info("Delete function execution time is {}".format(
            end_time - start_time))
