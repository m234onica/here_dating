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


def send_expired_message(pool):
    userId = pool.userId
    placeId = pool.placeId

    message.delete_menu(userId)
    return reply.quick_pair(userId, placeId, Context.wait_expired)


def delete(minutes):
    time_diff = expired_time(minutes)

    if minutes == Config.EXPIRED_TIME:
        expired_pool = filter.get_expired_pool(time_diff)

        if expired_pool == []:
            print("No expired pairing")
            return {"status_msg": "No expired pairing"}, 200

        for pool in expired_pool:
            pool.deletedAt = datetime.now()
            send_expired_message(pool)
            print("delete pairing:", pool)

    if minutes == Config.END_TIME:
        expired_data = filter.get_expired_pair(time_diff)

        if expired_data == []:
            print("No expired paired")
            return {"status_msg": "No expired paired"}, 200

        for data in expired_data:
            data.deletedAt = datetime.now()
            data.status = status_Enum(2)

            reply.timeout_message(data.playerA)
            reply.timeout_message(data.playerB)

            print("delete paired:", data)

    db_session.commit()
    print("delete success")
    return {"status_msg": "delete success."}, 200


def delete_here_dating(event, context):
    print("""This Function was triggered by messageId {} published at {} """.format(
        context.event_id, context.timestamp))

    if 'data' in event:
        minutes = base64.b64decode(event['data']).decode('utf-8')
        minutes = minutes.split(",")
        for minute in minutes:
            delete(int(minute))
            db_session.remove()
            print("expired minutes: ", minute)
    return "success"
