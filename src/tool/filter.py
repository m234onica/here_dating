from datetime import datetime, timedelta

from src.models import Pair, status_Enum
from src.db import db_session
from src.tool import message, reply
from src.func import api_request, response
from config import Config


def all_active_pair():
    return Pair.query.filter(Pair.deletedAt == None)


def get_pair(userId):
    return Pair.query.filter((Pair.playerA == userId) | (
        Pair.playerB == userId)).order_by(Pair.id.desc()).first()


def get_recipient_id(userId):
    pair = get_pair(userId)
    if pair.playerA == userId:
        recipient_id = pair.playerB
    else:
        recipient_id = pair.playerA

    return recipient_id


def get_persona_id():
    persona = api_request("GET", url="personas")
    if persona["data"] == []:
        response = message.persona()
        persona_id = response["id"]
    else:
        persona_id = persona["data"][0]["id"]

    return persona_id


def get_placeId(userId):
    pair = get_pair(userId)
    placeId = pair.placeId
    return placeId


def timeout(userId):
    pair = get_pair(userId)
    recipient_id = get_recipient_id(userId)
    now_time = datetime.now()

    if pair.startedAt != None and pair.deletedAt == None:
        if now_time - timedelta(minutes=Config.END_TIME) >= pair.startedAt:
            pair.deletedAt = now_time
            pair.status = status_Enum(2)

            db_session.commit()

            reply.timeout_message(userId)
            reply.timeout_message(recipient_id)

            return response(msg="Timeout to breaked pair", payload={"status": "timeout"}, code=200)

    return response(msg="User is chating", payload={"status": "paired"}, code=200)
