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
            sql = '''SELECT playerB FROM pair WHERE playerA="{userId}" AND deletedAt >= DATE_SUB(now(), INTERVAL {time} MINUTE) 
                    UNION ALL SELECT playerA FROM pair WHERE playerB="{userId}" AND deletedAt >= DATE_SUB(now(), INTERVAL {time} MINUTE); '''
            await cur.execute(sql.format(userId=userId, time=Config.RESET_PAIRING_TIME))
            has_paired_list = await cur.fetchall()

            accept_pairing_list = list.copy(user_list)
            for userId in has_paired_list:
                if userId[0] in accept_pairing_list:
                    accept_pairing_list.remove(userId[0])
            return accept_pairing_list[-1]
