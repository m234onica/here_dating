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


@api.route("/api/<userId>/placeName", methods=["GET"])
def place_name(userId):
    placeId = filter.get_place_id(userId)
    placeName = filter.get_place_name(placeId)
    return make_response({"status_msg": "Get place name", "placeName": placeName}, 200)


@api.route("/api/pair/<placeId>/<userId>", methods=["POST"])
def pair_user(placeId, userId):

    pool = filter.get_active_pool(userId)
    pair = filter.get_active_pair(userId)

    if status.is_place(placeId) == False:
        return response(msg="Wrong place ID.", payload={"status": "noPair"}, code=200)

    if status.is_noPair(userId):
        try:
            db_session.add(Pool(placeId=placeId, userId=userId))
        except:
            db_session.rollback()
            raise
        else:
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
    end_time = filter.get_pair_end_time(userId)
    
    pair = filter.get_pair(userId)

    if status.is_send_last_message(userId) == False:
        try:
            if pair.playerA == userId:
                pair.playerA_lastedAt = datetime.now()
            else:
                pair.playerB_lastedAt = datetime.now()
        except:
            db_session.rollback()
            raise
        else:
            db_session.commit()

        reply.last_message(userId, lastWord, end_time.hour,
                           end_time.minute, contact)

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
    try:
        if status.is_pairing(userId):
            data = filter.get_active_pool(userId)
            placeId = data.placeId
            words = Context.waiting_leave

        elif status.is_paired(userId):
            data = filter.get_active_pair(userId)
            data.status = status_Enum(1)

            placeId = data.placeId
            recipient_id = filter.get_recipient_id(userId)
            message.delete_menu(recipient_id)
            reply.quick_pair(recipient_id, placeId, Context.partner_leave_message)

            words = Context.leave_message

        data.deletedAt = datetime.now()
    except:
        db_session.rollback()
        raise
    else:
        db_session.commit()

    message.delete_menu(userId)
    return reply.quick_pair(userId, placeId, words)
