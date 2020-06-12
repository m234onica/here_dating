import asyncio
from src import delete

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(delete.main(loop))
    loop.run_until_complete(future)