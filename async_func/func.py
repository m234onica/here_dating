import requests
from urllib.parse import urlencode


def build_url(url: str, args: dict) -> str:
    params = urlencode(args)
    req = requests.models.PreparedRequest()
    req.prepare_url(url, params)
    return req.url
