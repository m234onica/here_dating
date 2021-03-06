import asyncio
from pair import pair
from delete import delete

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    future = [
        asyncio.ensure_future(pair.main(loop)),
        asyncio.ensure_future(delete.main(loop))
    ]
    loop.run_until_complete(asyncio.gather(*future))
