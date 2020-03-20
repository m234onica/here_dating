from flask import make_response
from datetime import datetime, timedelta

from src.models import Pair, status_Enum
from src.db import db_session
from src.tool import message, text
from config import END_TIME


def active_pair():
    return Pair.query.filter(Pair.deletedAt == None)


def recognize_player(userId):

    pair = Pair.query.filter((Pair.playerA == userId) | (
        Pair.playerB == userId)).order_by(Pair.id.desc()).first()

    if userId == pair.playerA:
        return "playerA"

    elif userId == pair.playerB:
        return "playerB"

    else:
        return None


def get_pair(player, userId):

    if player == "playerA":
        return Pair.query.filter(Pair.playerA == userId).order_by(
            Pair.id.desc()).first()

    elif player == "playerB":
        return Pair.query.filter(Pair.playerB == userId).order_by(
            Pair.id.desc()).first()
    else:
        return None


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

    persona = message.requests_get("/me/personas")
    persona_id = persona["data"][0]["id"]

    return persona_id


def timeout_chat(userId):
    player = recognize_player(userId)
    pair = get_pair(player, userId)
    now_time = datetime.now()

    if pair.startedAt != None and pair.deletedAt == None:
        if now_time - timedelta(minutes=END_TIME) >= pair.startedAt:
            pair.deletedAt = now_time
            pair.status = status_Enum(2)

            db_session.commit()

            persona_id = get_persona_id()
            message.push_text(id=userId, persona=persona_id,
                              text=text.timeout_text[0])
            message.push_multi_webview(
                id=userId, persona=persona_id,
                text=text.timeout_text[1], first_url=BASE_URL +
                "/message/" + userId,
                first_title=text.send_partner_last_message_button,
                sec_url=BASE_URL + "/intro", sec_title=text.pair_again_button)

            message.delete_menu(userId)

            return "timeout"

    else:
        return make_response({
            "status_msg": "User is chating",
            "payload": {
                "status": "paired"
            }}, 200)