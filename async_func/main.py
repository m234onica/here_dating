from src import pair
import base64
import asyncio
from config import Config


def main(event, context):
    print("""This Function was triggered by messageId {} published at {} """.format(
        context.event_id, context.timestamp))

    print("The current loop is running!")
    loop = asyncio.get_event_loop()
    future = [
        asyncio.ensure_future(pair.main(loop)),
        asyncio.ensure_future(delete.main(loop))
    ]
    loop.run_until_complete(asyncio.gather(*future))
    print(base64.b64decode(event['data']).decode('utf-8'))
    return "success"
