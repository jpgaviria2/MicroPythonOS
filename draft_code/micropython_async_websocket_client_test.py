# test of https://github.com/Vovaman/micropython_async_websocket_client/
# install with mip

import socket
import asyncio as a
import binascii as b
import random as r
from collections import namedtuple
import re
import struct
import ssl

from ws import AsyncWebsocketClient

async def websocket_example():
    # Initialize the WebSocket client
    aws = AsyncWebsocketClient(ms_delay_for_read=10)
    
    try:
        # Connect to echo.websocket.events
        await aws.handshake("wss://echo.websocket.events")
        print("Connected to WebSocket server")

        # Send a test message
        test_message = "Hello, WebSocket!"
        print(f"Sending: {test_message}")
        await aws.send(test_message)

        # Receive the echoed response
        response = await aws.recv()
        print(f"Received: {response}")

        # Send a ping
        aws.write_frame(ws.OP_PING, b"ping")
        print("Sent ping")

        # Wait for pong or other messages
        response = await aws.recv()
        if response is None:
            print("Received pong or connection closed")
        else:
            print(f"Received: {response}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        await aws.close()
        print("Connection closed")

# Run the example
a.run(websocket_example())
