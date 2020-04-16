from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for, make_response
from datetime import datetime, timedelta

from src.db import init_db, db_session
from src.models import Place, Pair, status_Enum
from src.tool import message, func, text
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

    persona_id = func.get_persona_id()

    active = func.active_pair()
    # userId is in active data
    is_player = active.filter((Pair.playerA == userId)
                              | (Pair.playerB == userId)).first()

    # 有userId但沒有開始時間：配對
    if is_player is not None:
        if is_player.startedAt == None:
            message.push_text(userId, persona_id, text.waiting_pair)
            return func.user_response(msg="User is exist and pairing.", status="pairing", code=200)

        # 有userId且有開始時間：聊天
        else:
            return func.user_response(msg="User is chatting.", status="paired", code=200)

    # userId not in data -> find a waiting userId
    waiting = active.filter(Pair.playerB == None).filter(Pair.placeId == placeId).\
        order_by(Pair.createdAt.asc()).order_by(Pair.id.asc()).first()

    if waiting is not None:
        waiting.playerB = userId
        waiting.startedAt = datetime.now()
        db_session.commit()

        recipient_id = func.get_recipient_id(userId)
        for words in text.waiting_success:
            message.push_quick_reply(userId, persona_id, words)
            message.push_quick_reply(recipient_id, persona_id, words)

        message.push_paired_menu(userId)
        message.push_paired_menu(recipient_id)
        return func.user_response(msg="Pairing success.", status="paired", code=200)

    else:
        db_session.add(Pair(placeId=placeId, playerA=userId))
        db_session.commit()

        message.push_pairing_menu(userId)
        message.push_text(userId, persona_id, text.waiting_pair)

        return func.user_response(msg="User start to pair.", status="pairing", code=200)
    return "success"


@api.route("/api/user/send", methods=["POST"])
def send_last_word():
    userId = request.json["userId"]
    lastWord = request.json["lastWord"]

    payload = get_status(userId).json
    status = payload["payload"]["status"]

    player = func.recognize_player(userId)
    pair = func.get_pair(player, userId)

    persona_id = func.get_persona_id()

    if status == "unSend":
        if player == "playerA":
            pair.playerA_lastedAt = datetime.now()

        elif player == "playerB":
            pair.playerB_lastedAt = datetime.now()

        db_session.commit()

        recipient_id = func.get_recipient_id(userId)
        message.push_text(recipient_id, persona_id,
                          text.partner_last_message + lastWord)
        message.push_text(userId, persona_id,
                          text.user_last_message + lastWord)

    return func.user_response(msg="Send palyer's last word.", status="success", code=200)


@api.route("/api/user/status/<userId>", methods=["GET"])
def get_status(userId):
    player = func.recognize_player(userId)
    pair = func.get_pair(player, userId)

    if pair == None:
        return func.user_response(msg="User does not pair.", status="noPair", code=200)

    if pair.deletedAt == None:
        if pair.startedAt == None:
            return func.user_response(msg="User is pairing", status="pairing", code=200)

        return func.user_response(msg="User is chating", status="paired", code=200)

    if pair.startedAt == None:
        return func.user_response(msg="User stop waiting", status="pairing_fail", code=200)

    if pair.deletedAt - timedelta(minutes=Config.END_TIME) < pair.startedAt:
        return func.user_response(msg="User leaved", status="leaved", code=200)

    if pair.deletedAt - timedelta(minutes=Config.END_TIME) >= pair.startedAt:

        if userId == pair.playerA:
            if pair.playerA_lastedAt == None:
                return func.user_response(msg="Timeout but not send last word.", status="unSend", code=200)

        if userId == pair.playerB:
            if pair.playerB_lastedAt == None:
                return func.user_response(msg="Timeout but not send last word.", status="unSend", code=200)

        return func.user_response(msg="User is pairing", status="noPair", code=200)


# 用戶離開聊天室
@api.route("/api/user/leave/<userId>", methods=["POST"])
def leave(userId):
    active = func.active_pair()
    pair = active.filter((Pair.playerA == userId) | (Pair.playerB == userId)).\
        filter(Pair.deletedAt == None).first()

    persona_id = func.get_persona_id()
    recipient_id = func.get_recipient_id(userId)

    if pair == None:
        return func.user_response(msg="User isn't in chatroom", status="noPair", code=200)

    pair.deletedAt = datetime.now()
    pair.status = status_Enum(1)
    db_session.commit()

    message.push_webview(
        id=userId, text=text.leave_message, persona=persona_id,
        webview_page="/pair.html", title=text.pair_again_button)

    message.delete_menu(userId)

    if recipient_id != None:
        message.push_webview(
            id=recipient_id, text=text.partner_leave_message, persona=persona_id,
            webview_page="/pair.html", title=text.pair_again_button)
        message.delete_menu(recipient_id)
    return "User leave"
