import asyncio
from queue import Queue
from typing import Optional, Union


class ReceivedRequests:
    def __init__(self, queue: Union[Queue, asyncio.Queue]):
        self.queue = queue
        self.received_requests: dict = {}

    def get(self, key: str, default: Optional[int] = None) -> Optional[int]:
        while not self.queue.empty():
            path = self.queue.get()
            self.received_requests[path] = self.received_requests.get(path, 0) + 1
        return self.received_requests.get(key, default)

    async def get_async(self, key: str, default: Optional[int] = None) -> Optional[int]:
        while not self.queue.empty():
            path = await self.queue.get()
            self.received_requests[path] = self.received_requests.get(path, 0) + 1
        return self.received_requests.get(key, default)
