from datetime import datetime, timedelta

from src.db import db_session
from src.models import status_Enum
from src.func import response
from src.tool import filter, reply
from config import Config


def timeout(userId):
    pair = filter.get_pair(userId)
    recipient_id = filter.get_recipient_id(userId)
    now_time = datetime.now()

    if pair.startedAt != None and pair.deletedAt == None:
        if now_time - timedelta(minutes=Config.END_TIME) >= pair.startedAt:
            pair.deletedAt = now_time
            pair.status = status_Enum(2)

            db_session.commit()

            reply.timeout_message(userId)
            reply.timeout_message(recipient_id)

            return response(msg="Timeout to breaked pair", payload={"status": "timeout"}, code=200)
    return response(msg="User is chating", payload={"status": "paired"}, code=200)