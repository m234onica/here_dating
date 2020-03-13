from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for, make_response
from sqlalchemy.sql.expression import literal
from datetime import datetime, timedelta

from src.db import init_db, db_session
from src.models import Place, Pair, status_Enum
from src.sdk import message

api = Blueprint("api", __name__)
init_db()


@api.route("/api/place/<placeId>", methods=["GET"])
def verify_distance(placeId):
    place = Place.query.filter_by(id=placeId).first()

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

# 配對用戶
@api.route("/api/user/pair", methods=["POST"])
def pair_user():
    userId = request.json["userId"]
    placeId = request.json["placeId"]

    active = Pair.query.filter(Pair.deletedAt == None) 
    # userId is in active data
    is_player = active.filter((Pair.playerA == userId) | (Pair.playerB == userId)).first()

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

        return make_response({
            "status_msg": "Pairing success.", 
            "payload": {
                "status": "paired"
            }}, 200)
    else:
        db_session.add( Pair(placeId=placeId, playerA=userId ) )
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

    pair = get_status(userId).json

    if pair["payload"]["status"] == "unSend":
        user = Pair.query.filter((Pair.playerA == userId) | (Pair.playerB == userId)).\
            filter(Pair.lastwordAt == None).order_by(Pair.id.desc()).first()

        user.lastwordAt = datetime.now()
        db_session.commit()
        
        return message.push_text(pair["payload"]["recipient_id"], None, "對面的鹹魚給你留了話：" + lastWord)

    else:
        return make_response({
            "status_msg": "Have been sended. Can't send it again", 
            "payload": {
                "status": "send"
                }
            }, 200)


@api.route("/api/user/status/<userId>", methods=["GET"])
def get_status(userId):
    pair = Pair.query.filter((Pair.playerA == userId) | (Pair.playerB == userId)).order_by(Pair.id.desc()).first()

    if userId != pair.playerA:
            recipient_id = pair.playerA
    else:
        recipient_id = pair.playerB

    if pair == None:
        return make_response({
            "status_msg": "User is pairing",
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
                "status": "paired",
                "recipient_id": recipient_id
            }}, 200)

    elif pair.deletedAt - timedelta(minutes=30) < pair.startedAt:
        return make_response({
            "status_msg": "User leaved",
            "payload": {
                "status": "leaved",
                "player": [pair.playerA, pair.playerB]
            }}, 200)

    elif pair.deletedAt - timedelta(minutes=30) >= pair.startedAt:
        if pair.lastwordAt == None:
            return make_response({
                "status_msg": "Timeout but not send last word.",
                "payload": {
                    "status": "unSend",
                    "recipient_id": recipient_id
                }}, 200)

        return make_response({
            "status_msg": "Timeout and not sended last word.",
            "payload": {
                "status": "send"
            }}, 200)


# 用戶離開聊天室
@api.route("/api/user/leave/<userId>", methods=["GET"])
def leave(userId):
    pair = Pair.query.filter((Pair.playerA == userId) | (Pair.playerB == userId)).\
        filter(Pair.deletedAt == None).first()

    if pair == None:
        return {"status_msg": "User isn't in chatroom"}, 200

    pair.deletedAt = datetime.now()
    pair.status = status_Enum(1)
    db_session.commit()
    return {"status_msg": "User leaved."}, 200
