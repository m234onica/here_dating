from datetime import datetime, timedelta

from src.db import db_session
from src.models import status_Enum
from src.func import response
from src.context import Context
from src.tool import filter, reply, message
from config import Config


def timeout(userId):
    pair = filter.get_active_pair(userId)
    recipient_id = filter.get_recipient_id(userId)
    now_time = datetime.now()
    if pair.startedAt == None and pair.playerB == None:
        if now_time - timedelta(minutes=Config.EXPIRED_TIME) < pair.createdAt:
            return response(msg="User is pairing", payload={"status": "pairing"}, code=200)
        else:
            pair.status = status_Enum(0)
            message.delete_menu(userId)
            reply.quick_pair(userId, pair.placeId, Context.wait_expired)
    else:
        if now_time - timedelta(minutes=Config.END_TIME) < pair.startedAt:
            return response(msg="User is paired", payload={"status": "paired"}, code=200)
        else:
            pair.status = status_Enum(2)
            reply.timeout_message(userId)
            reply.timeout_message(recipient_id)

    pair.deletedAt = now_time
    db_session.commit()

    return response(msg="Timeout to breaked pair", payload={"status": "pair_broken"}, code=200)

