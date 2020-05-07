import requests
import os
import json
from urllib.parse import urljoin
from src.tool import request
from src.tool.text import Context
from config import Config
from jinja2 import Environment, PackageLoader

json_file = Environment(loader=PackageLoader("src", "./static/data"))

def sender_action(id, action):
    template = json_file.get_template("data.json")
    rendered = template.module.sender_action(id=id, action=action)
    data = json.loads(rendered)
    return request.post("messages", data)


def push_text(id, persona, text):
    template = json_file.get_template("data.json")
    rendered = template.module.push_text(id=id, persona=persona, text=text)
    data = json.loads(rendered)
    return request.post("messages", data)


def push_quick_reply(id, persona, text):
    template = json_file.get_template("data.json")
    rendered = template.module.push_quick_reply(
        id=id, persona=persona, text=text)
    data = json.loads(rendered)
    return request.post("messages", data)


def push_attachment(id, persona, url):
    template = json_file.get_template("data.json")
    rendered = template.module.push_attachment(id=id, persona=persona, url=url)
    data = json.loads(rendered)
    return request.post("messages", data)


def push_button(id, persona, text, types, title, payload):
    buttons = []
    for i in range(len(types)):
        buttons.append(
            button_type(types=types[i], title=title[i], payload=payload[i])
        )

    data = {
        "recipient": {
            "id": id
        },
        "persona_id": persona,
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": text,
                    "buttons": buttons
                }
            }
        }
    }
    return request.post("messages", data)


def button_type(types, title, payload):
    url = urljoin(Config.STATIC_URL, payload)
    if types == None:
        return None

    if types == "web_url":
        return {
            "type": types,
            "title": title,
            "url": url,
            "messenger_extensions": True,
            "webview_height_ratio": "full"
        }

    if types == "postback":
        return {
            "type": types,
            "title": title,
            "payload": payload
        }


def get_started():
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}

    pair_url = urljoin(Config.STATIC_URL, "pair.html")
    rule_url = urljoin(Config.STATIC_URL, "rule.html")

    template = json_file.get_template("data.json")
    rendered = template.module.get_started(
        menu_start=Context.menu_start, pair_url=pair_url,
        menu_rule=Context.menu_rule, rule_url=rule_url)

    data = json.loads(rendered)
    get_start_responese = request.post("messenger_profile", data)

    whitelisted_domains = {
        "whitelisted_domains": [Config.BASE_URL, Config.STATIC_URL]}
    whitelisted_domains_response = request.post(
        "messenger_profile", whitelisted_domains)

    response = [get_start_responese, whitelisted_domains_response]
    return response


def push_customer_menu(id, postback_title):
    url = urljoin(Config.STATIC_URL, "rule.html")

    template = json_file.get_template("data.json")
    rendered = template.module.custom_menu(id=id,
                                           postback_title=postback_title,
                                           url_title=Context.menu_rule, url=url)
    data = json.loads(rendered)
    response = request.post("custom_user_settings", data)

    return response



def delete_menu(id):
    url = urljoin(Config.FB_API_URL, os.path.join(
        "me", "custom_user_settings"))

    params = {
        "psid": id,
        "params": '["persistent_menu"]',
        "access_token": Config.PAGE_ACCESS_TOKEN

    }
    response = requests.request("DELETE", url, params=params)
    print("delete_menu: ", response.json())
    return response


def persona():
    data = {
        "name": "系統訊息",
        "profile_picture_url": "https://storage.googleapis.com/here_dating/image/user_pic.png"
    }
    return request.post("personas", data)
