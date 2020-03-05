from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for, Response
from datetime import datetime, timedelta

from src.db import init_db, db_session
from src.models import Place, Pair, status_Enum

api = Blueprint('api', __name__)
init_db()


@api.route('/api/place/<int:placeId>', methods=["GET"])
def get_place_id(place_id):
    place = db_session.query(Place).filter_by(id=placeId).first()

    '''
    # 計算距離
    # 若在距離內，則回傳店名
    return {"status_msg": "succuss"}, 200
    # 若不在距離內，則回傳錯誤訊息
    return {"status_msg": "fail"}, 200
    # 若輸入店號不存在，則回傳錯誤訊息
    return {"status_msg": "not found"}, 404
    '''

# 配對用戶
@api.route('/api/pair', methods=["POST"])
def pair_users():
    userId = request.json['userId']
    placeId = request.json['placeId']

    pair_data = db_session.query(Pair)

    # 檢查此userId是否有配對過聊天室
    has_paired = pair_data.filter((Pair.playerA == userId) | (Pair.playerB == userId)).\
        filter(Pair.deletedAt == None).first()

    # 若沒有配對過
    if has_paired == None:

        # 查找等待中的配對
        pairing_player = pair_data.filter(Pair.playerB == None).\
            filter(Pair.deletedAt == None).\
            filter(Pair.placeId == placeId).first()

        # 若有，配對進去
        if pairing_player != None:
            pairing_player.playerB = userId
            pairing_player.startedAt = datetime.now()
            db_session.commit()
            return {"status_msg": "Paired success."}, 200

        # 若沒有，建立新的配對
        else:
            db_session.add(Pair(placeId=placeId, playerA=userId))
            db_session.commit()
            return {"status_msg": "Paired success. Please wait playerB"}, 200

    # 若用戶是playerA
    elif has_paired.playerA == userId:

        # 沒有playerB->配對中
        if has_paired.playerB == None:
            return {"status_msg": "This user is waiting."}, 200

        # 已經有playerB->已配對
        else:
            return {"status_msg": "This user is already paired."}, 200

    # 若用戶是playerB->已配對
    elif has_paired.playerB == userId:
        return {"status_msg": "This user is already paired."}, 200


# js定時戳這支API來更動該斷掉的配對狀態（等待到期＆聊天到期）
@api.route('/api/expired/<int:minutes>', methods=['GET'])
def expired(minutes):
    expired_time = datetime.now() - timedelta(minutes=minutes)

    # 等待到期的資料
    if minutes == 5:
        status = 0
        expired_data = db_session.query(Pair).filter(Pair.playerB == None).\
            filter(Pair.deletedAt == None).\
            filter(Pair.createdAt <= expired_time).all()

    # 聊天到期的資料
    if minutes == 10:
        status = 2
        expired_data = db_session.query(Pair).filter(Pair.playerB != None).\
            filter(Pair.deletedAt == None).\
            filter(Pair.startedAt <= expired_time).all()

    if expired_data == []:
        return {"status_msg": "No expired data"}, 200

    else:
        for expire in expired_data:
            expire.deletedAt = datetime.now()
            expire.status = status_Enum(status)
            db_session.commit()

        return {"status_msg": "delete success."}, 200


# 用戶離開聊天室
@api.route('/api/leave/<userId>', methods=['GET'])
def leave(userId):
    pair = db_session.query(Pair).filter((Pair.playerA == userId) | (Pair.playerB == userId)).\
        filter(Pair.deletedAt == None).first()

    if pair == None:
        return {"status_msg": "User isn't in chatroom"}, 200

    pair.deletedAt = datetime.now()
    pair.status = status_Enum(1)
    db_session.commit()
    return {"status_msg": "User leaved."}, 200
