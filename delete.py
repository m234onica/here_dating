from datetime import datetime, timedelta
import base64
import time

from src.db import db_session
from src.models import Pair, Pool, status_Enum
from src.tool import message, filter, reply
from src.func import expired_time
from src.context import Context
from config import Config

starttime = time.time()


def send_expired_message(userId):
    placeId = filter.get_place_id(userId)
    words = Context.wait_expired

    reply.quick_pair(userId, placeId, words)
    message.delete_menu(userId)

    return "sended success"


def send_end_message(userId):
    reply.timeout_message(userId)
    message.delete_menu(userId)
    return "sended success"


def delete(minutes):
    time_diff = expired_time(minutes)

    if minutes == Config.EXPIRED_TIME:
        active_pool = filter.all_active_pool()
        expired_data = active_pool.filter(Pool.createdAt <= time_diff).all()

        if expired_data == []:
            print("No expired data")
            return {"status_msg": "No expired data"}, 200

        for expired in expired_data:
            expired.deletedAt = datetime.now()
            print(send_expired_message(expired.userId))
            print("delete data:", expired)

    if minutes == Config.END_TIME:
        active_pair = filter.all_active_pair()
        expired_data = active_pair.filter(Pair.createdAt <= time_diff).all()

        if expired_data == []:
            print("No expired data")
            return {"status_msg": "No expired data"}, 200

        for expired in expired_data:
            expired.deletedAt = datetime.now()
            expired.status = status_Enum(2)

            send_end_message(expired.playerA)
            send_end_message(expired.playerB)

            print("delete data:", expired)

    db_session.commit()
    print("delete success")
    return {"status_msg": "delete success."}, 200


# def main(event, context):

#     print("""This Function was triggered by messageId {} published at {} """.format(
#         context.event_id, context.timestamp))

#     if 'data' in event:
#         minutes = base64.b64decode(event['data']).decode('utf-8')
#         minutes = minutes.split(",")
#         for minute in minutes:
#             delete(int(minute))
#             db_session.remove()
#             print("expired minutes: ", minute)
#     return "success"


if __name__ == '__main__':
    while True:
        delete(Config.EXPIRED_TIME)
        delete(Config.END_TIME)
        db_session.remove()
        time.sleep(60.0 - ((time.time() - starttime) % 60))
