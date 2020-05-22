from src.models import Pair, Pool
from src.tool import message
from src.func import api_request


def all_active_pool():
    return Pool.query.filter(Pool.deletedAt == None)


def get_active_pool(userId):
    return Pool.query.filter(Pool.userId == userId).filter(Pool.deletedAt == None).first()


def all_active_pair():
    return Pair.query.filter(Pair.deletedAt == None)


def get_pair(userId):
    return Pair.query.filter((Pair.playerA == userId) | (
        Pair.playerB == userId)).order_by(Pair.id.desc()).first()


def get_active_pair(userId):
    all_active = all_active_pair()
    return all_active.filter((Pair.playerA == userId) | (
        Pair.playerB == userId)).first()


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
    placeId = pair.placeId
    return placeId
