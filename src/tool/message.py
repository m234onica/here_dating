import requests
from src.tool import func
from src.tool.text import Context
from config import Config


def requests_post(url, payload):
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    post_url = func.concat(Config.FB_API_URL, "me", url)
    response = requests.request(
        "POST", url=post_url, params=params, json=payload).json()
    return response


def requests_get(url):
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}

    post_url = func.concat(Config.FB_API_URL, "me", url)
    response = requests.request("GET", url=post_url, params=params).json()

    # Debug才會用到的api
    if "error" in response.keys():
        post_url = func.concat(Config.FB_API_URL, url)
        response = requests.request("GET", url=post_url, params=params).json()
    return response


def sender_action(id, action):
    data = {
        "recipient": {
            "id": id
        },
        "sender_action": action
    }
    return requests_post("messages", data)


def push_text(id, persona, text):
    data = {
        "recipient": {
            "id": id
        },
        "persona_id": persona,
        "message": {
            "text": text
        }
    }
    return requests_post("messages", data)


def push_quick_reply(id, persona, text):
    data = {
        "recipient": {
            "id": id
        },
        "messaging_type": "RESPONSE",
        "persona_id": persona,
        "message": {
            "text": text,
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "Hi",
                    "payload": "Hi",
                }
            ]
        }
    }
    return requests_post("messages", data)


def push_attachment(id, persona, url):
    data = {
        "recipient": {
            "id": id
        },
        "persona_id": persona,
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "is_reusable": True,
                    "url": url
                }
            }
        }
    }
    return requests_post("messages", data)


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
    return requests_post("messages", data)


def button_type(types, title, payload):
    url = func.concat(Config.STATIC_URL, payload)
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

    whitelisted_domains = {
        "whitelisted_domains": [
            Config.BASE_URL,
            Config.STATIC_URL
        ]
    }

    pair_url = func.concat(Config.STATIC_URL, "pair.html")
    rule_url = func.concat(Config.STATIC_URL, "rule.html")
    data = {
        "get_started": {
            "payload": "Start"
        },
        "greeting": [
            {
                "locale": "default",
                "text": "我是問候語\n我是問候語我是問候語我是問候語\n我是問候語\n"
            }
        ],
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {
                        "type": "web_url",
                        "title": Context.menu_start,
                        "url": pair_url,
                        "messenger_extensions": True,
                        "webview_height_ratio": "full"
                    },
                    {
                        "type": "web_url",
                        "title": Context.menu_rule,
                        "url": rule_url,
                        "messenger_extensions": True,
                        "webview_height_ratio": "full"
                    }
                ]
            }
        ]
    }
    get_start_responese = requests_post("messenger_profile", data)
    whitelisted_domains_response = requests_post(
        "messenger_profile", whitelisted_domains)
    response = [get_start_responese, whitelisted_domains_response]
    return response


def push_pairing_menu(id):
    url = func.concat(Config.STATIC_URL, "rule.html")
    data = {
        "psid": id,
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {
                        "type": "postback",
                        "title": Context.menu_waiting_cancel,
                        "payload": "Leave"
                    },
                    {
                        "type": "web_url",
                        "title": Context.menu_rule,
                        "url": url,
                        "messenger_extensions": True,
                        "webview_height_ratio": "full"
                    }
                ]
            }
        ]
    }
    response = requests_post("custom_user_settings", data)
    print("pairing_menu:", response)
    return response


def push_paired_menu(id):
    url = func.concat(Config.STATIC_URL, "rule.html")
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
                        "url": url,
                        "messenger_extensions": True,
                        "webview_height_ratio": "full"
                    }
                ]
            }
        ]
    }
    response = requests_post("custom_user_settings", data)
    print("paired_menu: ", response)
    return response


def delete_menu(id):
    url = func.concat(Config.FB_API_URL, "me", "custom_user_settings")
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
    return requests_post("personas", data)
