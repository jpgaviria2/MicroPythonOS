import uasyncio
from collections import deque

class AsyncQueue:
    def __init__(self, maxlen=10):  # Set a default maximum length
        self._queue = deque((), maxlen, True)  # Initialize deque with specified maxlen
        self._event = uasyncio.Event()  # Event for signaling when items are added

    async def get(self, timeout=None):
        """Get an item from the queue, waiting if empty until an item is available or timeout expires."""
        while not self._queue:
            if timeout is not None:
                try:
                    await uasyncio.wait_for(self._event.wait(), timeout)  # Wait for item or timeout
                except uasyncio.TimeoutError:
                    raise Empty("Queue is empty and timed out")
            else:
                await self._event.wait()  # Wait indefinitely for an item
            self._event.clear()  # Clear event after waking up
        return self._queue.popleft()  # Return the item

    async def put(self, item):
        """Put an item in the queue and signal waiting coroutines."""
        self._queue.append(item)  # This will now work with proper maxlen
        self._event.set()  # Signal that an item is available

    def qsize(self):
        """Return the current size of the queue."""
        return len(self._queue)

    def empty(self):
        """Return True if the queue is empty."""
        return len(self._queue) == 0

class Empty(Exception):
    """Exception raised when queue is empty and non-blocking or timeout occurs."""
    pass
    

import uasyncio
#from async_queue import AsyncQueue, Empty  # Assuming the above code is in async_queue.py

async def producer(queue):
    for i in range(5):
        print(f"Producing {i}")
        await queue.put(i)
        await uasyncio.sleep(1)  # Simulate some delay

async def consumer(queue):
    while True:
        try:
            item = await queue.get(timeout=2.0)  # Wait up to 2 seconds
            print(f"Consumed {item}")
        except Empty:
            print("Consumer timed out waiting for item")
            break

async def main():
    queue = AsyncQueue()
    # Run producer and consumer concurrently in the event loop
    await uasyncio.gather(producer(queue), consumer(queue))

# Run the event loop
uasyncio.run(main())
