import requests
import os
import json
from urllib.parse import urljoin, urlencode
from jinja2 import Environment, PackageLoader

from src.func import api_request
from src.context import Context
from config import Config

json_file = Environment(loader=PackageLoader("src", "static/data"))
template = json_file.get_template("data.json.jinja")


def sender_action(id, action):
    rendered = template.module.sender_action(id=id, action=action)
    data = json.loads(rendered)
    return api_request("POST", urls=["me","messages"], json=data)


def push_text(id, persona, text):
    rendered = template.module.push_text(id=id, persona=persona, text=text)
    data = json.loads(rendered)
    return api_request("POST", urls=["me","messages"], json=data)


def push_quick_reply(id, persona, text):
    rendered = template.module.push_quick_reply(
        id=id, persona=persona, text=text)
    data = json.loads(rendered)
    return api_request("POST", urls=["me","messages"], json=data)


def push_attachment(id, persona, url):
    rendered = template.module.push_attachment(id=id, persona=persona, url=url)
    data = json.loads(rendered)
    return api_request("POST", urls=["me","messages"], json=data)


def push_button(id, persona, text, types, title, payload):
    rendered = template.module.push_button(
        id=id, persona=persona, text=text, types=types, payload=payload, title=title)
    data = json.loads(rendered)
    return api_request("POST", urls=["me","messages"], json=data)


def get_started():
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}

    pair_url = urljoin(Config.STATIC_URL, "pair.html")
    rule_url = urljoin(Config.STATIC_URL, "rule.html")

    rendered = template.module.get_started(
        username="{{user_first_name}}",
        menu_start=Context.menu_start, pair_url=pair_url,
        menu_rule=Context.menu_rule, rule_url=rule_url)

    data = json.loads(rendered)
    get_start_responese = api_request(
        "POST", urls=["me","messenger_profile"], json=data)

    whitelisted_domains = {
        "whitelisted_domains": [Config.BASE_URL, Config.STATIC_URL]}
    whitelisted_domains_response = api_request(
        "POST", urls=["me","messenger_profile"], json=whitelisted_domains)

    response = [get_start_responese, whitelisted_domains_response]
    return response


def push_customer_menu(id, postback_title):
    url = urljoin(Config.STATIC_URL, "rule.html")

    rendered = template.module.custom_menu(id=id,
                                           postback_title=postback_title,
                                           url_title=Context.menu_rule, url=url)
    data = json.loads(rendered)
    return api_request("POST", urls=["me","custom_user_settings"], json=data)


def delete_menu(id):
    params = {
        "psid": id,
        "params": '["persistent_menu"]',
        "access_token": Config.PAGE_ACCESS_TOKEN
    }
    return api_request("DELETE", urls=["me","custom_user_settings"], params=params)


def persona():
    rendered = template.module.persona()
    data = json.loads(rendered)
    return api_request("POST", urls=["me","personas"], json=data)


def get_username(userId):
    params = urlencode(
        {"fields": "first_name, last_name", "access_token": Config.PAGE_ACCESS_TOKEN})

    user_profile = api_request(
        "GET", urls=[userId], params=params)

    username = user_profile["last_name"] + user_profile["first_name"]
    return username
