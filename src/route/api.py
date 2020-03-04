from flask import Blueprint, render_template, jsonify, request, g, redirect, flash, url_for, Response
from src.db import init_db, db_session
from src.models import Place, Pair

api = Blueprint('api', __name__)
init_db()


@api.route('/api/place/<int:place_id>', methods=["GET"])
def get_place_id(place_id):
    place = db_session.query(Place).filter_by(id=place_id).first()

    '''
    # 計算距離
    # 若在距離內，則回傳店名
    return {"status_msg": "succuss"}, 200
    # 若不在距離內，則回傳錯誤訊息
    return {"status_msg": "fail"}, 200
    # 若輸入店號不存在，則回傳錯誤訊息
    return {"status_msg": "not found"}, 404
    '''