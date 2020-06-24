import os
import requests
import json
import asyncio
from urllib.parse import urljoin, urlencode
from jinja2 import Environment, PackageLoader
from config import Config
from context import Context
from func import build_url

FB_API_URL = "https://graph.facebook.com/v6.0"
url = urljoin(FB_API_URL, "/me/messages")
params = {"access_token": Config.PAGE_ACCESS_TOKEN}

json_file = Environment(loader=PackageLoader("delete", "static/data"))
template = json_file.get_template("data.json.jinja")


def get_persona_id():
    url = urljoin(FB_API_URL, "/me/personas")
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    persona = requests.get(url=url, params=params).json()
    return persona["data"][0]["id"]


persona_id = get_persona_id()
async def timeout_text(session, userId):
    rendered = template.module.push_text(
        id=userId, persona=persona_id, text=Context.timeout_text[0])
    data = json.loads(rendered)
    return await session.post(url, params=params, json=data)


async def timeout_button(session, pairId, userId):
    web_url = urljoin(Config.BASE_URL, "messeage.html")
    web_params = {"pairId": pairId, "userId": userId}
    payload = build_url(web_url, web_params)

    rendered = template.module.push_button(
        id=userId,
        persona=persona_id,
        text=Context.timeout_text[1],
        types="timeout",
        payload=[payload, "Quick_pair"],
        title=[Context.send_partner_last_message_button,
               Context.pair_again_button]
    )
    data = json.loads(rendered)

    await timeout_text(session, userId)
    return await session.post(url, params=params, json=data)


async def delet_pair_menu(session, pairId, userId):
    url = urljoin(FB_API_URL, "/me/custom_user_settings")
    params = {
        "psid": userId,
        "params": '["persistent_menu"]',
        "access_token": Config.PAGE_ACCESS_TOKEN
    }
    await timeout_button(session, pairId, userId)
    return await session.delete(url, params=params)


async def pool_button(session, placeId, userId):
    quick_pair_postback = "@".join(["Pair", placeId])
    general_pair_postback = "General_pair"

    rendered = template.module.push_button(
        id=userId,
        persona=persona_id,
        text=Context.wait_expired,
        types="quick_pair",
        payload=[quick_pair_postback, general_pair_postback],
        title=[Context.quick_pair_button, Context.pair_other_button]
    )
    data = json.loads(rendered)

    return await session.post(url, params=params, json=data)


async def delet_pool_menu(session, placeId, userId):
    url = urljoin(FB_API_URL, "/me/custom_user_settings")
    params = {
        "psid": userId,
        "params": '["persistent_menu"]',
        "access_token": Config.PAGE_ACCESS_TOKEN
    }
    await pool_button(session, placeId, userId)
    return await session.delete(url, params=params)
