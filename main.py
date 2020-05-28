import base64
from delete import delete
from src.db import db_session

def main(event, context):

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