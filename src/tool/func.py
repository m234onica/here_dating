import requests
from urllib.parse import urljoin
from flask import make_response
from datetime import datetime, timedelta

from src.models import Pair, status_Enum
from src.db import db_session
from src.tool import message
from config import Config


def all_active_pair():
    return Pair.query.filter(Pair.deletedAt == None)


def get_pair(userId):
    return Pair.query.filter((Pair.playerA == userId) | (
        Pair.playerB == userId)).order_by(Pair.id.desc()).first()


def get_player(userId):

    pair = Pair.query.filter((Pair.playerA == userId) | (
        Pair.playerB == userId)).order_by(Pair.id.desc()).first()

    if pair == None:
        return None

    if userId == pair.playerA:
        return "playerA"

    if userId == pair.playerB:
        return "playerB"


def get_pairId(userId):
    pair = get_pair(userId)
    return str(pair.id)


def get_recipient_id(userId):

    player = get_player(userId)
    pair = get_pair(userId)
    if player == "playerA":
        recipient_id = pair.playerB

    elif player == "playerB":
        recipient_id = pair.playerA
    else:
        recipient_id = None

    return recipient_id


def get_persona_id():
    params = {"access_token": Config.PAGE_ACCESS_TOKEN}
    api_url = urljoin(Config.FB_API_URL, "me", "personas")
    persona = requests.request("GET", url=api_url, params=params).json()

    if persona["data"] == []:
        response = message.persona()
        persona_id = response["id"]
    else:
        persona_id = persona["data"][0]["id"]

    return persona_id


def get_placeId(userId):
    pair = get_pair(userId)
    if pair != None:
        placeId = pair.placeId
        return placeId
    else:
        return None


def user_response(msg, payload, code):
    response = make_response({
        "status_msg": msg,
        "payload": payload
    }, code)
    return response
