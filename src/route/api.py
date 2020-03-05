from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for, Response
from src.db import init_db, db_session
from src.models import Place, Pair

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
            pairint_player.startedAt = datetime.now()
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
