from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for, make_response
from datetime import datetime, timedelta

from src.db import init_db, db_session
from src.models import Place, Pair, status_Enum
from src.tool import message, func
from config import END_TIME

api = Blueprint("api", __name__)
init_db()


@api.route("/api/place/<placeId>", methods=["GET"])
def verify_distance(placeId):
    place = Place.query.filter(Place.id == placeId).first()

    # 若輸入店號不存在，則回傳錯誤訊息
    if place is None:
        return make_response({"status_msg": "Not found", "payload": False}, 404)

    """
    # 計算距離
    # 若在距離內，則回傳店名
    return {"status_msg": "succuss"}, 200
    # 若不在距離內，則回傳錯誤訊息
    return {"status_msg": "fail"}, 200
    """
    return make_response({"status_msg": "Get placeId", "payload": True, "placeId": place.id}, 200)

@api.route("/api/user/pair", methods=["POST"])
def pair_user():
    userId = request.json["userId"]
    placeId = request.json["placeId"]

    persona = message.requests_get("/me/personas")
    persona_id = persona["data"][0]["id"]

    active = Pair.query.filter(Pair.deletedAt == None)
    # userId is in active data
    is_player = active.filter((Pair.playerA == userId)
                              | (Pair.playerB == userId)).first()

    # 有userId但沒有開始時間：配對
    if is_player is not None:
        if is_player.startedAt == None:
            return make_response({
                "status_msg": "User is exist and pairing.",
                "payload": {
                    "status": "pairing"
                }}, 200)

        # 有userId且有開始時間：聊天
        else:
            return make_response({
                "status_msg": "User is chatting.",
                "payload": {
                    "status": "paired"
                }}, 200)

    # userId not in data -> find a waiting userId
    waiting = active.filter(Pair.playerB == None).filter(Pair.placeId == placeId).\
        order_by(Pair.createdAt.asc()).order_by(Pair.id.asc()).first()

    if waiting is not None:
        waiting.playerB = userId
        waiting.startedAt = datetime.now()
        db_session.commit()

        message.push_text(userId, persona_id, "配對成功，可以開始聊天囉！")

        recipient_id = func.get_recipient_id(userId)
        message.push_text(recipient_id, persona_id, "配對成功，可以開始聊天囉！")
        
        return make_response({
            "status_msg": "Pairing success.",
            "payload": {
                "status": "paired"
            }}, 200)
    else:
        db_session.add(Pair(placeId=placeId, playerA=userId))
        db_session.commit()

        return make_response({
            "status_msg": "User start to pair.",
            "payload": {
                "status": "pairing"
            }}, 200)


@api.route("/api/user/send", methods=["POST"])
def send_last_word():
    userId = request.json["userId"]
    lastWord = request.json["lastWord"]

    payload = get_status(userId).json
    status = payload["payload"]["status"]

    player = func.recognize_player(userId)
    pair = func.get_pair(player, userId)

    persona = message.requests_get("/me/personas")
    persona_id = persona["data"][0]["id"]

    if status == "unSend":
        if player == "playerA":
            pair.playerA_lastedAt = datetime.now()

        elif player == "playerB":
            pair.playerB_lastedAt = datetime.now()

        db_session.commit()

        recipient_id = func.get_recipient_id(userId)
        message.push_text(recipient_id, persona_id, "對面的鹹魚給你留了話：" + lastWord)
        message.push_text(userId, persona_id, "發送留言成功。")

    return make_response({
        "status_msg": "Send palyer's last word.",
        "payload": {
            "status": "success"
        }}, 200)


@api.route("/api/user/status/<userId>", methods=["GET"])
def get_status(userId):
    player = func.recognize_player(userId)
    pair = func.get_pair(player, userId)

    if pair == None:
        return make_response({
            "status_msg": "User does not pair.",
            "payload": {
                "status": "noPair"
            }}, 200)


    if pair.startedAt == None:
        return make_response({
            "status_msg": "User is pairing",
            "payload": {
                "status": "pairing"
            }}, 200)

    elif pair.deletedAt == None:
        return make_response({
            "status_msg": "User is chating",
            "payload": {
                "status": "paired"
            }}, 200)

    elif pair.deletedAt - timedelta(minutes=END_TIME) < pair.startedAt:
        return make_response({
            "status_msg": "User leaved",
            "payload": {
                "status": "leaved",
            }}, 200)

    elif pair.deletedAt - timedelta(minutes=END_TIME) >= pair.startedAt:

        if userId == pair.playerA:
            if pair.playerA_lastedAt == None:
                return make_response({
                    "status_msg": "Timeout but not send last word.",
                    "payload": {
                        "status": "unSend",
                    }}, 200)

        if userId == pair.playerB:
            if pair.playerB_lastedAt == None:
                return make_response({
                    "status_msg": "Timeout but not send last word.",
                    "payload": {
                        "status": "unSend",
                    }}, 200)

        return make_response({
            "status_msg": "User is pairing",
            "payload": {
            "status": "noPair"
        }}, 200)


# 用戶離開聊天室
@api.route("/api/user/leave/<userId>", methods=["POST"])
def leave(userId):
    active = func.active_pair()
    pair = active.filter((Pair.playerA == userId) | (Pair.playerB == userId)).\
        filter(Pair.deletedAt == None).first()

    if pair == None:
        return make_response({
            "status_msg": "User isn't in chatroom",
            "payload": {
                "status": "noPair",
            }}, 200)

    pair.deletedAt = datetime.now()
    pair.status = status_Enum(1)
    db_session.commit()

    return make_response({
        "status_msg": "User leaved.",
        "payload": {
            "status": "leaved",
        }}, 200)
