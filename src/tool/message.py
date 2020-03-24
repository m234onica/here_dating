import requests
from src.tool import text
from config import PAGE_ACCESS_TOKEN, FB_API_URL, BASE_URL

message_api_url = FB_API_URL + "/me/messages"


def requests_post(url, payload):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    return requests.request("POST", url=url, params=params, json=payload).json()


def requests_get(url):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    return requests.request("GET", url=FB_API_URL + url, params=params).json()


def sender_action(id, action):
    data = {
            "recipient": {
                "id": id
            },
            "sender_action": action
    }
    return requests_post(message_api_url, data)


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
    return requests_post(message_api_url, data)


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
    return requests_post(message_api_url, data)


def push_webview(id, persona, text, webview_page, title):
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
                    "buttons": [
                        {
                            "type": "web_url",
                            "url": BASE_URL + webview_page,
                            "messenger_extensions": True,
                            "title": title,
                            "webview_height_ratio": "full"
                        }
                    ]

                }
            }
        }
    }
    return requests_post(message_api_url, data)


def push_multi_webview(id, persona, text, first_url, first_title, sec_url, sec_title):
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
                    "buttons": [
                        {
                            "type": "web_url",
                            "url": first_url,
                            "messenger_extensions": True,
                            "title": first_title,
                            "webview_height_ratio": "full"
                        },
                        {
                            "type": "web_url",
                            "url": sec_url,
                            "messenger_extensions": True,
                            "title": sec_title,
                            "webview_height_ratio": "full"
                        }
                    ]

                }
            }
        }
    }
    return requests_post(message_api_url, data)


def get_started():
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
                        "type": "postback",
                        "title": text.menu_start,
                        "payload": "Start_pair"
                    },
                    {
                        "type": "web_url",
                        "title": text.menu_rule,
                        "url": BASE_URL + "/rule",
                        "messenger_extensions": True,
                        "webview_height_ratio": "full"
                    }
                ]
            }
        ]
    }
    return requests_post(
        FB_API_URL + "/me/messenger_profile", data)


def push_chat_menu(id):
    data = {
        "psid": id,
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {
                        "type": "postback",
                        "title": text.menu_leave,
                        "payload": "Leave"
                    }
                ]
            }
        ]
    }
    return requests_post(
        FB_API_URL + "/me/custom_user_settings", data)


def push_waiting_menu(id):
    data = {
        "psid": id,
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {
                        "type": "postback",
                        "title": "離開等待",
                        "payload": "Leave"
                    }
                ]
            }
        ]
    }
    return requests_post(
        FB_API_URL + "/me/custom_user_settings", data)


def delete_menu(id):
    url = FB_API_URL + '/me/custom_user_settings'
    params = {
        "psid": id,
        "params": '["persistent_menu"]',
        "access_token": PAGE_ACCESS_TOKEN

    }

    return requests.request("DELETE", url, params=params)


def persona():
    data = {
        "name": "系統訊息",
        "profile_picture_url": "https://storage.googleapis.com/satellite-l5yx88bg3/robo.png"
    }
    return requests_post(FB_API_URL + "/me/personas", data)
