import ssl
import certifi
import json
import asyncio
import aiomysql
import aiohttp
import requests
from urllib.parse import urljoin
from jinja2 import Environment, PackageLoader

from config import mysql, Config
from src.context import Context

json_file = Environment(loader=PackageLoader("src", "static/data"))

def get_persona_id():
    url = urljoin(Config.FB_API_URL, "/me/personas")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    persona = requests.get(url=url, params=params).json()
    return persona["data"][0]["id"]


async def push_text(session, id):
    url = urljoin(Config.FB_API_URL, "/me/messages")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    persona_id = get_persona_id()

    template = json_file.get_template("data.json.jinja")
    rendered = template.module.push_text(
        id=id, persona=persona_id, text=Context.waiting_success[0])
    data = json.loads(rendered)

    async with session.post(url, params=params, json=data) as response:
        return await response.text()


async def push_quick_reply(session, id):
    url = urljoin(Config.FB_API_URL, "/me/messages")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    persona_id = get_persona_id()

    template = json_file.get_template("data.json.jinja")
    rendered = template.module.push_quick_reply(
        id=id, persona=persona_id, text=Context.waiting_success[1])
    data = json.loads(rendered)

    async with session.post(url, params=params, json=data) as response:
        return await response.text()


async def push_customer_menu(session, id):
    url = urljoin(Config.FB_API_URL, "/me/custom_user_settings")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    static_url = urljoin(Config.STATIC_URL, "rule.html")

    template = json_file.get_template("data.json.jinja")
    rendered = template.module.custom_menu(id=id,
                                           postback_title=Context.menu_leave,
                                           url_title=Context.menu_rule, url=static_url)
    data = json.loads(rendered)

    async with session.post(url, params=params, json=data) as response:
        return await response.text()


async def pair(conn):
    user_list = []
    async with conn.cursor() as cur:
        try:
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

                length = len(user)

                if length % 2 != 0:
                    length -= 1
                for id in range(0, length, 2):
                    pair = '''INSERT INTO pair(placeId, playerA, playerB) values ({}, {}, {})'''
                    placeId = group[i][0]
                    playerA = user[id]
                    playerB = user[id+1]

                    user_list.append(playerA)
                    user_list.append(playerB)

                    await cur.execute(pair.format(placeId, playerA, playerB))
                    # await conn.commit()

                    pool = ''' UPDATE pool set deletedAt=CURRENT_TIME(), status=1 WHERE userId={} and deletedAt is NULL;'''
                    await cur.execute(pool.format(user[id]))
                    await cur.execute(pool.format(user[id+1]))
                    result = await cur.fetchall()
            await conn.commit()

        except BaseException as err:
            await conn.rollback()
            raise err

    conn.close()
    return user_list


async def pool(loop):
    conn = await aiomysql.connect(host=mysql["host"], port=3306, user=mysql["username"], password=mysql["password"], db=mysql["database"], loop=loop)
    user_list = await pair(conn)
    sslcontext = ssl.create_default_context(cafile=certifi.where())

    for id in user_list:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=sslcontext)) as session:
            await push_text(session, id)
            await push_quick_reply(session, id)
            await push_customer_menu(session, id)
    return user_list

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(pool(loop))


