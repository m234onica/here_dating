from datetime import datetime, timedelta
import base64
import time

from src.db import db_session
from src.models import Pair, status_Enum
from src.tool import message, func, text
from config import Config

starttime = time.time()


def send_expired_message(userId):
    persona_id = func.get_persona_id()

    message.delete_menu(userId)
    message.push_webview(
        id=userId, text=text.wait_expired,
        persona=persona_id, webview_page="/pair", title=text.pair_again_button)
    return "sended success"


def send_end_message(userId):
    persona_id = func.get_persona_id()
    pairId = func.get_pairId(userId)
    message.delete_menu(userId)
    message.push_text(id=userId, persona=persona_id,
                      text=text.timeout_text[0])

    message.push_multi_button(
        id=userId,
        persona=persona_id,
        text=text.timeout_text[1],
        types=["web_url", "web_url"],
        payload=["/" + pairId + "/message/" + userId, "/pair"],
        title=[text.send_partner_last_message_button, text.pair_again_button]
    )
    return "sended success"


def delete(minutes):

    active_data = func.active_pair()
    expired_time = datetime.now() - timedelta(minutes=minutes)

    if minutes == Config.EXPIRED_TIME:
        status = 0
        expired_data = active_data.filter(Pair.startedAt == None).\
            filter(Pair.createdAt <= expired_time).all()

    if minutes == Config.END_TIME:
        status = 2
        expired_data = active_data.filter(Pair.playerB != None).\
            filter(Pair.startedAt <= expired_time).all()

    if expired_data == []:
        print("No expired data")
        return {"status_msg": "No expired data"}, 200

    for expired in expired_data:
        expired.deletedAt = datetime.now()
        expired.status = status_Enum(status)

        if expired.playerB == None:
            send_expired_message(expired.playerA)

        else:
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
