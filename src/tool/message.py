import requests
from src.tool import text
from config import Config


def requests_post(url, payload):
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    post_url = "/".join([Config.FB_API_URL, "me", url])
    response = requests.request("POST", url=post_url, params=params, json=payload).json()
    return response


def requests_get(url):
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}

    post_url = "/".join([Config.FB_API_URL, "me", url])
    response = requests.request("GET", url=post_url, params=params).json()

    #Debug才會用到的api
    if "error" in response.keys():
        post_url = "/".join([Config.FB_API_URL, url])
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
                            "url": Config.BASE_URL + webview_page,
                            "messenger_extensions": True,
                            "title": title,
                            "webview_height_ratio": "full"
                        }
                    ]

                }
            }
        }
    }
    return requests_post("messages", data)


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
                            "url": Config.BASE_URL + first_url,
                            "messenger_extensions": True,
                            "title": first_title,
                            "webview_height_ratio": "full"
                        },
                        {
                            "type": "web_url",
                            "url": Config.BASE_URL + sec_url,
                            "messenger_extensions": True,
                            "title": sec_title,
                            "webview_height_ratio": "full"
                        }
                    ]

                }
            }
        }
    }
    return requests_post("messages", data)


def push_multi_button(id, persona, text, first_title, payload, url, sec_title):
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
                            "type": "postback",
                            "title": first_title,
                            "payload": payload

                        },
                        {
                            "type": "web_url",
                            "url": url,
                            "messenger_extensions": True,
                            "title": Config.BASE_URL + sec_title,
                            "webview_height_ratio": "full"
                        }
                    ]

                }
            }
        }
    }
    return requests_post("messages", data)


def get_started():
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    
    whitelisted_domains = {
        "whitelisted_domains": [
            Config.BASE_URL
        ]
    }

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
                        "title": text.menu_start,
                        "url": Config.BASE_URL + "/pair",
                        "messenger_extensions": True,
                        "webview_height_ratio": "full"
                    },
                    {
                        "type": "web_url",
                        "title": text.menu_rule,
                        "url": Config.BASE_URL + "/rule",
                        "messenger_extensions": True,
                        "webview_height_ratio": "full"
                    }
                ]
            }
        ]
    }
    get_start_responese = requests_post("messenger_profile", data)
    whitelisted_domains_response = requests_post("messenger_profile", whitelisted_domains)
    response = [get_start_responese, whitelisted_domains_response]
    return response


def push_pairing_menu(id):
    data = {
        "psid": id,
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {
                        "type": "postback",
                        "title": text.menu_waiting_cancel,
                        "payload": "Leave"
                    },
                    {
                        "type": "web_url",
                        "title": text.menu_rule,
                        "url": Config.BASE_URL + "/rule",
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
    response = requests_post("custom_user_settings", data)
    print("paired_menu: ", response)
    return response


def delete_menu(id):
    url = Config.FB_API_URL + '/me/custom_user_settings'
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
        "profile_picture_url": "https://storage.googleapis.com/here_dating/user_pic.png"
    }
    return requests_post("personas", data)
