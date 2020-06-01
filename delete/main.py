from delete import delete
import base64

from src.db import db_session
from src import message
from config import Config


def main(event, context):
    print("""This Function was triggered by messageId {} published at {} """.format(
        context.event_id, context.timestamp))

    delete(Config.EXPIRED_TIME)
    delete(Config.END_TIME)
    db_session.remove()

    return "success"
