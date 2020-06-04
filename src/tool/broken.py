from datetime import datetime, timedelta

from src.db import db_session
from src.models import status_Enum
from src.func import response, expired_time
from src.context import Context
from src.tool import filter, reply, message, status
from config import Config


def timeout(userId):
    pair = filter.get_active_pair(userId)
    pool = filter.get_active_pool(userId)

    if status.is_pairing(userId):
        time_diff = expired_time(Config.EXPIRED_TIME)

        if time_diff >= pool.createdAt:
            try:
                pool.deletedAt = datetime.now()
            except:
                db_session.rollback()
                raise
            else:
                db_session.commit()

            message.delete_menu(userId)
            reply.quick_pair(userId, pool.placeId, Context.wait_expired)
        else:
            return response(msg="User is pairing", payload={"status": "pairing"}, code=200)

    else:
        time_diff = expired_time(Config.END_TIME)

        if time_diff >= pair.createdAt:
            try:
                pair.deletedAt = datetime.now()
                pair.status = status_Enum(2)
            except:
                db_session.rollback()
                raise
            else:
                db_session.commit()

            recipient_id = filter.get_recipient_id(userId)
            reply.timeout_message(userId)
            reply.timeout_message(recipient_id)
        else:
            return response(msg="User is paired", payload={"status": "paired"}, code=200)

    return response(msg="Timeout to breaked pair", payload={"status": "pair_broken"}, code=200)
