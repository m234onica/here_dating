import os
import requests
from urllib.parse import urljoin
from datetime import datetime, timedelta
from flask import make_response

from config import Config


def api_request(method, urls, json=None, params={"access_token": Config.PAGE_ACCESS_TOKEN}): 
    url = urljoin(Config.FB_API_URL,  "/".join(urls))
    response = requests.request(
        method=method, url=url, params=params, json=json).json()
    return response


def response(msg, payload, code):
    response = make_response({
        "status_msg": msg,
        "payload": payload
    }, code)
    return response


def expired_time(minutes):
    return datetime.now() - timedelta(minutes=minutes)
