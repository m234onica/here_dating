from pytz import timezone
from datetime import datetime

from src.models import Place, Pair, Pool
from src.tool import message
from src.func import api_request, expired_time


def all_active_pool():
    return Pool.query.filter(Pool.deletedAt == None)


def get_active_pool(userId):
    return Pool.query.filter(Pool.userId == userId).filter(Pool.deletedAt == None).first()


def get_expired_pool(time_diff):
    return Pool.query.filter(Pool.deletedAt == None).filter(Pool.createdAt <= time_diff).all()


def all_active_pair():
    return Pair.query.filter(Pair.deletedAt == None)


def get_pool(userId):
    return Pool.query.filter(Pool.userId == userId).order_by(Pool.id.desc()).first()


def get_pair(userId):
    return Pair.query.filter((Pair.playerA == userId) | (
        Pair.playerB == userId)).order_by(Pair.id.desc()).first()


def get_active_pair(userId):
    all_active = all_active_pair()
    return all_active.filter((Pair.playerA == userId) | (
        Pair.playerB == userId)).first()


def get_expired_pair(time_diff):
    return Pair.query.filter(Pair.deletedAt == None).filter(Pair.createdAt <= time_diff).all()


def get_pair_end_time(userId):
    pair = get_pair(userId)
    end_dt = pair.deletedAt
    return end_dt.astimezone(timezone("Asia/Taipei"))


def get_recipient_id(userId):
    pair = get_pair(userId)
    if pair.playerA == userId:
        recipient_id = pair.playerB
    else:
        recipient_id = pair.playerA

    return recipient_id


def get_persona_id():
    persona = api_request("GET", urls=["me", "personas"])
    if persona["data"] == []:
        response = message.persona()
        persona_id = response["id"]
    else:
        persona_id = persona["data"][0]["id"]

    return persona_id


def get_place_id(userId):
    pair = get_pair(userId)
    if pair == None:
        return None
    else:
        placeId = pair.placeId
        return placeId


def get_place_name(placeId):
    place = Place.query.filter(Place.id == placeId).first()
    return place.name
