from flask import make_response
from datetime import datetime, timedelta

from src.models import Pair, status_Enum
from src.db import db_session
from src.tool import message, text, reply
from config import Config


def active_pair():
    return Pair.query.filter(Pair.deletedAt == None)


def recognize_player(userId):

    pair = Pair.query.filter((Pair.playerA == userId) | (
        Pair.playerB == userId)).order_by(Pair.id.desc()).first()

    if pair == None:
        return None

    if userId == pair.playerA:
        return "playerA"

    if userId == pair.playerB:
        return "playerB"


def get_pair(player, userId):

    if player == "playerA":
        return Pair.query.filter(Pair.playerA == userId).order_by(
            Pair.id.desc()).first()

    elif player == "playerB":
        return Pair.query.filter(Pair.playerB == userId).order_by(
            Pair.id.desc()).first()
    else:
        return None


def get_pairId(userId):
    player = recognize_player(userId)
    pair = get_pair(player, userId)
    return str(pair.id)


def get_recipient_id(userId):

    player = recognize_player(userId)

    if player == "playerA":
        pair = get_pair(player, userId)
        recipient_id = pair.playerB

    elif player == "playerB":
        pair = get_pair(player, userId)
        recipient_id = pair.playerA
    else:
        recipient_id = None

    return recipient_id


def get_persona_id():

    persona = message.requests_get("personas")
    if persona["data"] == []:
        message.persona()
    persona_id = persona["data"][0]["id"]

    return persona_id


def timeout_chat(userId):
    player = recognize_player(userId)
    pair = get_pair(player, userId)
    recipient_id = get_recipient_id(userId)
    now_time = datetime.now()

    if pair.startedAt != None and pair.deletedAt == None:
        if now_time - timedelta(minutes=Config.END_TIME) >= pair.startedAt:
            pair.deletedAt = now_time
            pair.status = status_Enum(2)

            db_session.commit()

            reply.timeout(userId)
            message.delete_menu(userId)

            reply.timeout(recipient_id)
            message.delete_menu(recipient_id)

            return user_response(msg="Timeout to breaked pair", payload={"status": "timeout"}, code=200)

    return user_response(msg="User is chating", payload={"status": "paired"}, code=200)


def get_placeId(userId):
    pair = get_pair(recognize_player(userId), userId)
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
