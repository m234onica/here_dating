from datetime import datetime, timedelta
import schedule
import time

from src.db import db_session
from src.models import Pair
from config import EXPIRED_TIME, END_TIME


def delete(minutes):
    expired_time = datetime.now() - timedelta(minutes=minutes)

    # 等待到期的資料
    if minutes == EXPIRED_TIME:
        status = 0
        expired_data = Pair.query.filter(Pair.playerB == None).\
            filter(Pair.deletedAt == None).\
            filter(Pair.createdAt <= expired_time).all()

    # 聊天到期的資料
    if minutes == END_TIME:
        status = 2
        expired_data = Pair.query.filter(Pair.playerB != None).\
            filter(Pair.deletedAt == None).\
            filter(Pair.startedAt <= expired_time).all()

    if expired_data == []:
        print("delete expired success")
        return {"status_msg": "No expired data"}, 200

    else:
        for expire in expired_data:
            expire.deletedAt = datetime.now()
            expire.status = status_Enum(status)
            db_session.commit()
        print("delete end success")
        return {"status_msg": "delete success."}, 200



schedule.every(1).minutes.do(delete, EXPIRED_TIME)
schedule.every(1).minutes.do(delete, END_TIME)

while True:
    schedule.run_pending()
    time.sleep(1)