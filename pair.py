import asyncio
import aiomysql
import aiohttp
from urllib.parse import urljoin

from config import Config
from src.tool import reply, filter
from src.context import Context



async def push_paired_text(session, id):
    url = urljoin(Config.FB_API_URL, "/me/messages")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    persona_id = filter.get_persona_id()

    data = {
        "recipient": {
            "id": id
        },
        "persona_id": persona_id,
        "message": {
            "text": Context.waiting_success[0]
        }
    }

    async with session.post(url, params=params, json=data) as response:
        return response.text()


async def push_quick_reply(session, id):
    url = urljoin(Config.FB_API_URL, "/me/messages")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    persona_id = filter.get_persona_id()

    data = {
        "recipient": {
            "id": id
        },

        "persona_id": persona_id,
        "messaging_type": "RESPONSE",
        "message": {
            "text": Context.waiting_success[1],
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "Hi",
                    "payload": "Hi"
                }
            ]
        }

    }

    async with session.post(url, params=params, json=data) as response:
        return response.text()


async def push_menu(session, id):
    url = urljoin(Config.FB_API_URL, "/me/custom_user_settings")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    static_url = urljoin(Config.STATIC_URL, "rule.html")

    data = {
        "psid": id,
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {
                        "type": "postback",
                        "title": Context.menu_leave,
                        "payload": "Leave"
                    },
                    {
                        "type": "web_url",
                        "title": Context.menu_rule,
                        "url": static_url,
                        "messenger_extensions": True,
                        "webview_height_ratio": "full"
                    }
                ]
            }
        ]
    }
    async with session.post(url, params=params, json=data) as response:
        return response.text()


async def pair(conn):
    user_list = []
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
            user_list.append(user)

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
    return user_list


async def pool(loop):
    conn = await aiomysql.connect(host=Config.HOST, port=Config.PORT, user=Config.USER, password=Config.PASSWORD, db=Config.NAME, loop=loop)
    user_list = await pair(conn)

    for group in user_list:
        for id in group:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                await push_paired_text(session, id)
                await push_quick_reply(session, id)
                await push_menu(session, id)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(pool(loop))
