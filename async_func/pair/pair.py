import ssl
import certifi
import asyncio
import aiomysql
import aiohttp
import logging
import warnings
from urllib.parse import urljoin
from datetime import datetime, timedelta
from config import mysql, Config
from pair import message, select

warnings.filterwarnings("ignore", category=aiomysql.Warning)
logging.basicConfig(
    format='%(asctime)s %(levelname)s - %(message)s', level=logging.INFO)


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
                if int(count[1]) > 56:
                    status = 1
                    logging.warning(
                        "PlaceId: {} was cut by GROUP_CONCAT()".format(count[0]))
            return status


async def pair(loop, pool):
    message_list = []
    data = []
    reset_list = []

    group = await select.all_pairing(loop, pool)
    for i in range(len(group)):
        placeId = group[i][0]
        pairing_list = group[i][1].split(",")
        while len(pairing_list) > 1:
            playerA = pairing_list[0]
            playerB = await select.filter_accept_pairing(loop, pool, playerA, pairing_list)
            if playerB != playerA:
                message_list.append(playerA)
                message_list.append(playerB)
                data.append((placeId, playerA, playerB),)

                pairing_list.remove(playerB)

            else:
                reset = await select.reset_pairing(loop, pool, placeId)
                if playerA in reset:
                    reset_list.append(playerA)
            pairing_list.remove(playerA)
        while len(reset_list) > 1:

            playerA, playerB = reset_list[:2]

            message_list.append(playerA)
            message_list.append(playerB)
            data.append((placeId, playerA, playerB),)

            reset_list.remove(playerA)
            reset_list.remove(playerB)

    pair_sql = '''INSERT INTO pair (placeId, playerA, playerB) values (%s, %s, %s);'''
    pool_sql = '''UPDATE pool set deletedAt=CURRENT_TIME(), status=1 WHERE placeId=%s and userId=%s and deletedAt is NULL;
                UPDATE pool set deletedAt=CURRENT_TIME(), status=1 WHERE userId=%s and deletedAt is NULL;'''

    tasks = [
        asyncio.create_task(
            insert(loop=loop, sql=pair_sql, data=data, pool=pool)),
        asyncio.create_task(
            insert(loop=loop, sql=pool_sql, data=data, pool=pool))
    ]

    result = await asyncio.gather(*tasks)
    return message_list


async def main(loop):
    start_time = datetime.now()

    pool = await aiomysql.create_pool(host=mysql["host"], port=3306, user=mysql["username"], password=mysql["password"], db=mysql["database"], loop=loop)
    message_list = []
    status = await unpair_count(loop, pool)
    message_list = await pair(loop, pool)

    while status == 1:
        message_list = await pair(loop, pool)
        status = await unpair_count(loop, pool)

    pool.close()
    await pool.wait_closed()

    sslcontext = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=sslcontext)) as session:
        tasks = []
        for userId in message_list:
            task = asyncio.create_task(message.customer_menu(session, userId))
            tasks.append(task)
        await asyncio.gather(*tasks)

    end_time = datetime.now()
    logging.info("Pairing function execution time is {}".format(
        end_time - start_time))
