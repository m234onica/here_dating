import requests
import json
import asyncio
from urllib.parse import urljoin
from jinja2 import Environment, PackageLoader
from config import Config
from src.context import Context

json_file = Environment(loader=PackageLoader("src", "static/data"))


def get_persona_id():
    url = urljoin(Config.FB_API_URL, "/me/personas")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    persona = requests.get(url=url, params=params).json()
    return persona["data"][0]["id"]


async def text(session, userId):
    url = urljoin(Config.FB_API_URL, "/me/messages")
    persona_id = get_persona_id()

    template = json_file.get_template("data.json.jinja")
    rendered = template.module.push_text(
        id=userId, persona=persona_id, text=Context.waiting_success[0])
    data = json.loads(rendered)
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    return await session.post(url, params=params, json=data)


async def quick_reply(session, userId):
    url = urljoin(Config.FB_API_URL, "/me/messages")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    persona_id = get_persona_id()

    template = json_file.get_template("data.json.jinja")
    rendered = template.module.push_quick_reply(
        id=userId, persona=persona_id, text=Context.waiting_success[1])
    data = json.loads(rendered)
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    await text(session, userId)
    return await session.post(url, params=params, json=data)


async def customer_menu(session, userId):
    url = urljoin(Config.FB_API_URL, "/me/custom_user_settings")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    static_url = urljoin(Config.STATIC_URL, "rule.html")

    template = json_file.get_template("data.json.jinja")
    rendered = template.module.custom_menu(id=userId,
                                           postback_title=Context.menu_leave,
                                           url_title=Context.menu_rule, url=static_url)
    data = json.loads(rendered)
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    await quick_reply(session, userId)
    return await session.post(url, params=params, json=data)
