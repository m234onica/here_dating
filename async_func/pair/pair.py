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
from pair import message

warnings.filterwarnings("ignore", category=aiomysql.Warning)
logging.basicConfig(
    format='%(asctime)s %(levelname)s - %(message)s', level=logging.INFO)


async def select(loop, pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            group = []
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
            return await cur.fetchall()


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


async def unpaired_list(loop, pool, userId, user_list):
    recipient_list = []
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            sql = '''SELECT playerB FROM pair WHERE playerA="{userId}" 
                    UNION ALL SELECT playerA FROM pair WHERE playerB="{userId}";'''
            await cur.execute(sql.format(userId=userId))
            data = await cur.fetchall()
            recipient_list = list.copy(user_list)
            for d in data:
                if d[0] in recipient_list:
                    recipient_list.remove(d[0])
            recipient_list.remove(userId)
            return recipient_list


async def last_pairing_time(loop, pool, userId):
    now_time = datetime.now()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            sql = ''' SELECT deletedAt FROM pool WHERE userId="{userId}" ORDER BY deletedAt DESC LIMIT 1;'''
            await cur.execute(sql.format(userId=userId))
            deletedAt = await cur.fetchone()
            if deletedAt[0] is None:
                return None
            elif deletedAt[0] <= now_time - timedelta(minutes=Config.RESET_PAIRING_TIME):
                return True
            else:
                return False


async def pair(loop, pool):
    user_list = []
    data = []
    pair_opportunity = 0

    group = await select(loop, pool)
    for i in range(len(group)):
        user = group[i][1].split(",")
        while len(user) > 1:
            playerA = user[0]
            recipient_list = await unpaired_list(loop, pool, playerA, user)
            if recipient_list != []:
                placeId = group[i][0]
                playerB = recipient_list[0]

                user_list.append(playerA)
                user_list.append(playerB)
                data.append((placeId, playerA, playerB),)

                user.remove(playerA)
                user.remove(playerB)
            else:
                user.remove(playerA)
                pair_opportunity += 1
                continue

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
    return user_list, pair_opportunity


async def main(loop):
    start_time = datetime.now()

    pool = await aiomysql.create_pool(host=mysql["host"], port=3306, user=mysql["username"], password=mysql["password"], db=mysql["database"], loop=loop)
    user_list = []
    status = await unpair_count(loop, pool)
    user_list, pair_opportunity = await pair(loop, pool)

    while status == 1:
        user_list, pair_opportunity = await pair(loop, pool)
        status = await unpair_count(loop, pool)

    pool.close()
    await pool.wait_closed()

    sslcontext = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=sslcontext)) as session:
        tasks = []
        for userId in user_list:
            task = asyncio.create_task(message.customer_menu(session, userId))
            tasks.append(task)
        await asyncio.gather(*tasks)

    end_time = datetime.now()
    logging.info("Pairing function execution time is {}".format(
        end_time - start_time))
