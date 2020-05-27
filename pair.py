import json
import asyncio
import aiomysql
import aiohttp
from urllib.parse import urljoin
from jinja2 import Environment, PackageLoader

from config import Config
from src.tool import reply, filter
from src.context import Context

json_file = Environment(loader=PackageLoader("src", "static/data"))


async def push_paired_text(session, id):
    url = urljoin(Config.FB_API_URL, "/me/messages")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    persona_id = filter.get_persona_id()

    template = json_file.get_template("data.json.jinja")
    rendered = template.module.push_text(
        id=id, persona=persona_id, text=Context.waiting_success[0])
    data = json.loads(rendered)


    async with session.post(url, params=params, json=data) as response:
        return response.text()


async def push_quick_reply(session, id):
    url = urljoin(Config.FB_API_URL, "/me/messages")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    persona_id = filter.get_persona_id()

    template = json_file.get_template("data.json.jinja")
    rendered = template.module.push_quick_reply(
        id=id, persona=persona_id, text=Context.waiting_success[1])
    data = json.loads(rendered)

    async with session.post(url, params=params, json=data) as response:
        return response.text()


async def push_menu(session, id):
    url = urljoin(Config.FB_API_URL, "/me/custom_user_settings")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    static_url = urljoin(Config.STATIC_URL, "rule.html")

    template = json_file.get_template("data.json.jinja")
    rendered = template.module.custom_menu(id=id,
                                           postback_title=Context.menu_leave,
                                           url_title=Context.menu_rule, url=static_url)
    data = json.loads(rendered)

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
