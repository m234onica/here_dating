from datetime import datetime, timedelta
import base64
import time
import logging

from src.db import db_session
from src.models import Pair, Pool, status_Enum
from src import message, filter, reply
from src.func import expired_time
from src.context import Context
from config import Config

starttime = time.time()
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.WARNING)


def send_expired_message(pool):
    userId = pool.userId
    placeId = pool.placeId

    message.delete_menu(userId)
    return reply.quick_pair(userId, placeId, Context.wait_expired)


def delete(minutes):
    time_diff = expired_time(minutes)
    try:

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
    except BaseException as err:
        db_session.rollback()
        logging.error("SQL is rollback. error is: {}", err)
        raise err
    else:
        db_session.commit()

    print("delete success")
    return {"status_msg": "delete success."}, 200
