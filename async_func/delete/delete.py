import ssl
import certifi
import asyncio
import aiomysql
import aiohttp
import logging

from config import mysql, Config
from delete import message


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


async def delete(loop, pool):
    # For update sql
    all_poolId = []
    all_pairId = []
    # For messenger
    pool_data = []
    pair_data = []
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            pool_expired_sql = '''
                        SELECT id, placeId, userId
                        FROM pool
                        WHERE deletedAt is NULL AND createdAt <= CURRENT_TIME() - INTERVAL {} MINUTE;'''

            pair_expired_sql = ''' 
                        SELECT id, playerA
                        FROM pair
                        WHERE deletedAt is NULL AND createdAt <= CURRENT_TIME() - INTERVAL 3 MINUTE
                        UNION ALL
                        SELECT id, playerB
                        FROM pair
                        WHERE deletedAt is NULL AND createdAt <= CURRENT_TIME() - INTERVAL 3 MINUTE;'''

            await cur.execute(pool_expired_sql.format(Config.EXPIRED_TIME))
            pool_datas = await cur.fetchall()

            for data in pool_datas:
                all_poolId.append(data[0])
                pool_data.append(data[1:])

            await cur.execute(pair_expired_sql.format(Config.END_TIME, Config.END_TIME))
            pair_data = await cur.fetchall()
            pair_data = [list(row) for row in pair_data]

            for data in pair_data:
                all_pairId.append(data[0])
            all_pairId = list(set(all_pairId))

            delete_pool_sql = '''UPDATE pool set deletedAt=CURRENT_TIME() WHERE id=%s and deletedAt is NULL;'''
            delete_pair_sql = '''UPDATE pair set deletedAt=CURRENT_TIME(), status='end' WHERE id=%s and deletedAt is NULL;'''

            tasks = [
                asyncio.create_task(
                    update(loop=loop, sql=delete_pool_sql, data=all_poolId, pool=pool)),
                asyncio.create_task(
                    update(loop=loop, sql=delete_pair_sql, data=all_pairId, pool=pool))
            ]
            result = await asyncio.gather(*tasks)
        return pool_data, pair_data


async def main(loop):
    pool = await aiomysql.create_pool(host=mysql["host"], port=3306, user=mysql["username"], password=mysql["password"], db=mysql["database"], loop=loop)
    pool_data, pair_data = await delete(loop, pool)
    pool.close()
    await pool.wait_closed()

    sslcontext = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=sslcontext)) as session:
        pool_tasks = []
        pair_tasks = []

        for data in pool_data:
            task = asyncio.create_task(
                message.delet_pool_menu(session, data[0], data[1]))
            pool_tasks.append(task)

        for data in pair_data:
            task = asyncio.create_task(
                message.delet_pair_menu(session, data[0], data[1]))
            pair_tasks.append(task)

        return await asyncio.gather(*pool_tasks, *pair_tasks)
