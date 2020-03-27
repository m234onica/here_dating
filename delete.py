from datetime import datetime, timedelta
import time

from src.db import db_session
from src.models import Pair, status_Enum
from src.tool import message, func, text
from config import EXPIRED_TIME, END_TIME

starttime = time.time()

def get_active_data():
    active_data = Pair.query.filter(Pair.deletedAt == None)
    return active_data


def delete(minutes):
    
    active_data = get_active_data()
    expired_time = datetime.now() - timedelta(minutes=minutes)
    persona_id = func.get_persona_id()
    
    # 等待到期的資料
    if minutes == EXPIRED_TIME:
        status = 0
        words = text.wait_expired
        expired_data = active_data.filter(Pair.playerB == None).\
            filter(Pair.createdAt <= expired_time).all()

    # 聊天到期的資料
    if minutes == END_TIME:
        status = 2
        words = text.timeout_text
        expired_data = active_data.filter(Pair.playerB != None).\
            filter(Pair.startedAt <= expired_time).all()

    if expired_data == []:
        print("No expired data")
        return {"status_msg": "No expired data"}, 200

    else:
        for expire in expired_data:
            expire.deletedAt = datetime.now()
            expire.status = status_Enum(status)
            db_session.commit()

            message.delete_menu(expire.playerA)
            message.push_webview(
                id=expire.playerA, text=words,
                persona=persona_id, webview_page="/pair", title=text.pair_again_button)
            if expire.playerB is not None:
                message.delete_menu(expire.playerB)
                message.push_webview(
                    id=expire.playerB, text=words,
                    persona=persona_id, webview_page="/pair", title=text.pair_again_button)

            print("delete data:", expire)

        print("delete success")
        return {"status_msg": "delete success."}, 200

if __name__ == '__main__':
    while True:
        delete(EXPIRED_TIME)
        delete(END_TIME)
        db_session.remove()
        time.sleep(60.0 - ((time.time() - starttime) % 60))
