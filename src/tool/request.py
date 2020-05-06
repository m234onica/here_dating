import requests
from urllib.parse import urljoin
from config import Config


def post(url, payload):
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    post_url = urljoin(Config.FB_API_URL, "me", url)
    response = requests.request(
        "POST", url=post_url, params=params, json=payload).json()
    return response
