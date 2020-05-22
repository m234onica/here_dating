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
    message.delete_menu(userId)

    placeId = filter.get_place_id(userId)
    return reply.quick_pair(userId, placeId, Context.wait_expired)


def delete(minutes):
    time_diff = expired_time(minutes)

    if minutes == Config.EXPIRED_TIME:
        active_pool = filter.all_active_pool()
        expired_data = active_pool.filter(Pool.createdAt <= time_diff).all()

        if expired_data == []:
            print("No expired pairing")
            return {"status_msg": "No expired pairing"}, 200

        for expired in expired_data:
            expired.deletedAt = datetime.now()
            print(send_expired_message(expired.userId))
            print("delete pairing:", expired)

    if minutes == Config.END_TIME:
        active_pair = filter.all_active_pair()
        expired_data = active_pair.filter(Pair.createdAt <= time_diff).all()

        if expired_data == []:
            print("No expired paired")
            return {"status_msg": "No expired paired"}, 200

        for expired in expired_data:
            expired.deletedAt = datetime.now()
            expired.status = status_Enum(2)

            reply.timeout_message(expired.playerA)
            reply.timeout_message(expired.playerB)

            print("delete paired:", expired)

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
