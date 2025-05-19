import uasyncio as asyncio
import sys
from contextlib import suppress
import aiohttp
import _thread

# Shared buffer for input lines
input_buffer = []
lock = _thread.allocate_lock()  # Thread-safe access to buffer

# Thread function to read input and add to buffer
def read_input_thread():
    while True:
        line = input()
        with lock:
            input_buffer.append(line)
        if line == "exit":
            break

async def start_client(url: str) -> None:
    name = input("Please enter your name: ")

    # Start the input reading thread
    _thread.start_new_thread(read_input_thread, ())

    async def dispatch(ws: aiohttp.ClientWebSocketResponse) -> None:
        while True:
            #msg = await ws.receive()
            msg = await ws.__anext__()

            if msg.type is aiohttp.WSMsgType.TEXT:
                print("Text: ", msg.data.strip())
            elif msg.type is aiohttp.WSMsgType.BINARY:
                print("Binary: ", msg.data)
            elif msg.type is aiohttp.WSMsgType.PING:
                await ws.pong()
            elif msg.type is aiohttp.WSMsgType.PONG:
                print("Pong received")
            else:
                if msg.type is aiohttp.WSMsgType.CLOSE:
                    await ws.close()
                elif msg.type is aiohttp.WSMsgType.ERROR:
                    print("Error during receive %s" % ws.exception())
                elif msg.type is aiohttp.WSMsgType.CLOSED:
                    pass
                break

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            dispatch_task = asyncio.create_task(dispatch(ws))

            # Poll the input buffer instead of to_thread
            while True:
                line = None
                with lock:
                    if input_buffer:  # Check if there's input
                        line = input_buffer.pop(0)  # Get the first line
                if line:
                    await ws.send_str(name + ": " + line)
                    if line == "exit":  # Stop on "exit"
                        break
                await asyncio.sleep_ms(100)  # Avoid busy-waiting

            dispatch_task.cancel()
            with suppress(asyncio.CancelledError):
                await dispatch_task

# Run the client
asyncio.run(start_client("wss://echo.websocket.events"))
