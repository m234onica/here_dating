from pair import pool
import base64
import asyncio
from config import Config


def main(event, context):
    print("""This Function was triggered by messageId {} published at {} """.format(
        context.event_id, context.timestamp))

    print("The current loop is running!")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(pool(loop))
    print(base64.b64decode(event['data']).decode('utf-8'))
    return "success"
