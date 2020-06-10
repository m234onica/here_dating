import asyncio
from src import pair

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(pair.main(loop))
    loop.run_until_complete(future)
