import asyncio
import aiomysql
from urllib.parse import urljoin
from config import Config


async def all_pairing(loop, pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            group = []
            get_pool_data = ''' SELECT placeId,
                                GROUP_CONCAT(userId ORDER BY rand() SEPARATOR ",") as userId
                                FROM pool
                                WHERE deletedAt is NULL 
                                AND createdAt > CURRENT_TIME() - INTERVAL {} MINUTE
                                GROUP BY placeId; '''
            await cur.execute(get_pool_data.format(Config.EXPIRED_TIME))
            return await cur.fetchall()


async def filter_accept_pairing(loop, pool, userId, user_list):
    accept_pairing_list = []
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            sql = '''SELECT playerB FROM pair WHERE playerA="{userId}" 
                    UNION ALL SELECT playerA FROM pair WHERE playerB="{userId}";'''
            await cur.execute(sql.format(userId=userId))
            has_paired_list = await cur.fetchall()

            accept_pairing_list = list.copy(user_list)
            for userId in has_paired_list:
                if userId[0] in accept_pairing_list:
                    accept_pairing_list.remove(userId[0])
            return accept_pairing_list[-1]


async def reset_pairing(loop, pool, placeId):
    reset_list = []
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            sql = '''SELECT userId
                    FROM (SELECT userId, MAX(deletedAt) AS deletedAt FROM pool WHERE status=1 and placeId={placeId} GROUP BY userId) AS last_pool
                    WHERE deletedAt <= DATE_SUB(current_time(), INTERVAL {time} MINUTE) 
                    ORDER BY RAND();'''
            await cur.execute(sql.format(placeId=placeId, time=Config.RESET_PAIRING_TIME))
            data = await cur.fetchall()
            for d in data:
                reset_list.append(d[0])
    return reset_list
