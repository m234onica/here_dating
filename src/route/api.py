from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for, make_response
from datetime import datetime, timedelta

from src.db import init_db, db_session
from src.models import Place, Pair, status_Enum
from src.func import response
from src.tool import message, filter, reply, status
from src.tool.text import Context
from config import Config

api = Blueprint("api", __name__)
init_db()


@api.route("/api/place/<placeId>", methods=["GET"])
def verify_distance(placeId):
    place = Place.query.filter(Place.id == placeId).first()

    # 若輸入店號不存在，則回傳錯誤訊息
    if place is None:
        return make_response({"status_msg": "Not found", "payload": False}, 200)

    """
    # 計算距離
    # 若在距離內，則回傳店名
    return {"status_msg": "succuss"}, 200
    # 若不在距離內，則回傳錯誤訊息
    return {"status_msg": "fail"}, 200
    """
    return make_response({"status_msg": "Get placeId", "payload": True, "placeId": place.id}, 200)


@api.route("/api/pair/<placeId>/<userId>", methods=["POST"])
def pair_user(placeId, userId):

    # userId is in active data
    is_player = filter.get_active_pair(userId)

    # 有userId但沒有開始時間：配對
    if is_player is not None:
        if is_player.startedAt == None:
            reply.pairing(userId)
            return response(msg="User is exist and pairing.", payload={"status": "pairing"}, code=200)

        # 有userId且有開始時間：聊天
        else:
            return response(msg="User is chatting.", payload={"status": "paired"}, code=200)

    # userId not in data -> find a waiting userId
    active = filter.all_active_pair()
    waiting = active.filter(Pair.playerB == None).filter(Pair.placeId == placeId).\
        order_by(Pair.createdAt.asc()).order_by(Pair.id.asc()).first()

    if waiting is not None:
        waiting.playerB = userId
        waiting.startedAt = datetime.now()
        db_session.commit()

        recipient_id = filter.get_recipient_id(userId)

        reply.paired(userId)
        reply.paired(recipient_id)

        return response(msg="Pairing success.", payload={"status": "paired"}, code=200)

    else:
        db_session.add(Pair(placeId=placeId, playerA=userId))
        db_session.commit()

        reply.pairing(userId)
        message.push_customer_menu(userId, Context.menu_waiting_cancel)

        return response(msg="User start to pair.", payload={"status": "pairing"}, code=200)
    return "success"


@api.route("/api/user/send", methods=["POST"])
def send_last_word():
    userId = request.json["userId"]
    lastWord = request.json["lastWord"]

    payload = get_status(userId).json
    status = payload["payload"]["status"]

    pair = filter.get_pair(userId)

    if status == "unSend":
        if pair.playerA == userId:
            pair.playerA_lastedAt = datetime.now()
        else:
            pair.playerB_lastedAt = datetime.now()

        db_session.commit()

        reply.last_message(userId, lastWord)

    return response(msg="Send palyer's last word.", payload={"status": "success"}, code=200)


@api.route("/api/user/status/<userId>", methods=["GET"])
def get_status(userId):
    pair = filter.get_pair(userId)

    if pair == None:
        return response(msg="User does not pair.", payload={"status": "noPair"}, code=200)

    if status.is_pairing(pair):
        payload = {"status": "pairing", "pairId": pair.id}
        return response(msg="User is pairing", payload=payload, code=200)

    elif status.is_pair_fail(pair):
        payload = {"status": "pairing_fail", "pairId": pair.id}
        return response(msg="User stop waiting", payload=payload, code=200)

    elif status.is_paired(pair):
        payload = {"status": "paired", "pairId": pair.id}
        return response(msg="User is chating", payload=payload, code=200)

    elif status.is_leaved(pair):
        payload = {"status": "leaved", "pairId": pair.id}
        return response(msg="User leaved", payload=payload, code=200)

    else:
        if status.is_send_last_message(userId) is False:
            payload = {"status": "unSend", "pairId": pair.id}
            return response(msg="Timeout but not send last word.", payload=payload, code=200)

        payload = {"status": "noPair", "pairId": pair.id}
        return response(msg="User does not pair.", payload=payload, code=200)


# 用戶離開聊天室
@api.route("/api/user/leave/<userId>", methods=["POST"])
def leave(userId):
    pair = filter.get_active_pair(userId)
    recipient_id = filter.get_recipient_id(userId)

    if pair == None:
        return response(msg="User isn't in chatroom", payload={"status": "noPair"}, code=200)

    pair.deletedAt = datetime.now()
    pair.status = status_Enum(1)
    db_session.commit()

    placeId = filter.get_place_id(userId)
    words = Context.leave_message
    reply.quick_pair(userId, placeId, words.format(placeId=placeId))
    message.delete_menu(userId)

    if recipient_id != None:
        words = Context.partner_leave_message
        reply.quick_pair(recipient_id, placeId, words.format(placeId=placeId))
        message.delete_menu(recipient_id)
    return "User leave"
