from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for, make_response
from datetime import datetime, timedelta

from src.db import init_db, db_session
from src.models import Place, Pair, Pool, status_Enum
from src.func import response
from src.tool import message, filter, reply, status
from src.context import Context
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

    pool = filter.get_active_pool(userId)
    pair = filter.get_active_pair(userId)

    if status.is_noPair(userId):
        db_session.add(Pool(placeId=placeId, userId=userId))
        db_session.commit()

        reply.pairing(userId)
        message.push_customer_menu(userId, Context.menu_waiting_cancel)

        return response(msg="User start to pair.", payload={"status": "pairing"}, code=200)

    elif status.is_pairing(userId):
        reply.pairing(userId)
        return response(msg="User is exist and pairing.", payload={"status": "pairing"}, code=200)

    else:
        return response(msg="User is chatting.", payload={"status": "paired"}, code=200)

    return "success"


@api.route("/api/user/send", methods=["POST"])
def send_last_word():
    userId = request.json["userId"]
    lastWord = request.json["lastWord"]
    contact = request.json["contact"]
    current_time = datetime.now()

    payload = get_status(userId).json
    status = payload["payload"]["status"]

    pair = filter.get_pair(userId)

    if status == "unSend":
        if pair.playerA == userId:
            pair.playerA_lastedAt = datetime.now()
        else:
            pair.playerB_lastedAt = datetime.now()

        db_session.commit()

        reply.last_message(userId, lastWord, current_time.hour, current_time.minute, contact)

    return response(msg="Send palyer's last word.", payload={"status": "success"}, code=200)


@api.route("/api/user/status/<userId>", methods=["GET"])
def get_status(userId):
    pair = filter.get_pair(userId)

    if pair == None:
        return response(msg="User does not pair.", payload={"status": "noPair"}, code=200)

    if status.is_pairing(userId):
        payload = {"status": "pairing", "pairId": pair.id}
        return response(msg="User is pairing", payload=payload, code=200)

    elif status.is_paired(userId):
        payload = {"status": "paired", "pairId": pair.id}
        return response(msg="User is chating", payload=payload, code=200)

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

    placeId = pair.placeId
    message.delete_menu(userId)

    if recipient_id == None:
        words = Context.waiting_leave
        reply.quick_pair(userId, placeId, words)

    else:
        words = Context.leave_message
        reply.quick_pair(userId, placeId, words)

        words = Context.partner_leave_message
        reply.quick_pair(recipient_id, placeId, words)
        message.delete_menu(recipient_id)
    return "User leave"
