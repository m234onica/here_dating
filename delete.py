import time
from flask import Flask, g
from datetime import datetime, timedelta

from src.db import init_db, db_session
from src.models import Place, Pair, status_Enum


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object("config")
BASE_URL = app.config.get('BASE_URL')


@app.context_processor
def url():
    return {'base_url': g.url, 'version': g.version}


@app.before_request
def before_req():
    g.url = BASE_URL
    g.version = time.time()


@app.route('/api/expired/user/<int:minutes>', methods=['GET'])
def expire(minutes):
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


if __name__ == '__main__':
    app.run()
