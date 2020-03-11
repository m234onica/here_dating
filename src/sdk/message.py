import requests
from config import PAGE_ACCESS_TOKEN, FB_API_URL, BASE_URL

message_api_url = FB_API_URL + "/me/messages?access_token=" + PAGE_ACCESS_TOKEN
quick_message = [
    {
        "content_type": "text",
        "title": "Leave",
        "payload": "leave",
    },
    {
        "content_type": "text",
        "title": "Hello",
        "payload": "Hello",
    }
]


def requests_post(url, payload):
    return requests.post(url, json=payload).json


def push_text(id, persona, text):
    data = {
        "recipient": {
            "id": id
        },
        "persona_id": persona,
        "message": {
            "text": text,
            "quick_replies": quick_message
        }
    }
    return requests_post(message_api_url, data)


def push_webview(id, text, webview_page):
    data = {
        "recipient": {
            "id": id
        },
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
                            "title": "Intro",
                            "webview_height_ratio": "full"
                        }
                    ]

                }
            },
            "quick_replies": quick_message
        }
    }
    return requests_post(message_api_url, data)


def push_menu(id):
    data = {
        "psid": id,
        "persistent_menu":[
            {
            "locale":"default",
            "composer_input_disabled": False,
            "call_to_actions":[
                {
                "title":"My Account",
                "type":"nested",
                "call_to_actions":[
                    {
                    "type":"web_url",
                    "url": BASE_URL + "/intro",
                    "messenger_extensions": True,
                    "title": "離開聊天...",
                    "webview_height_ratio": "full"
                    }
                ]
                }
            ]
            }
        ]
    }
    return requests_post(
        FB_API_URL + "/me/custom_user_settings?access_token=" + PAGE_ACCESS_TOKEN, data)


def persona():
    data = {
        "name": "You Know Who",
        "profile_picture_url": "https://storage.googleapis.com/satellite-l5yx88bg3/53.png"
    }
    return requests_post( FB_API_URL + "/me/personas?access_token=" + PAGE_ACCESS_TOKEN, data)
