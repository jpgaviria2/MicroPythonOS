# example from https://github.com/micropython/micropython-lib/blob/master/python-ecosys/aiohttp/examples/ws.py
# works with:
# import mip
# mip.install("aiohttp")
# but only on esp32 target, not unix?!

import sys
import ssl

# ruff: noqa: E402
sys.path.insert(0, ".")
import aiohttp
import asyncio

try:
    URL = sys.argv[1]  # expects a websocket echo server
except Exception:
    # URL = "ws://echo.websocket.events" # also works
    URL = "wss://echo.websocket.events"


sslctx = False

if URL.startswith("wss:"):
    try:
        sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        sslctx.verify_mode = ssl.CERT_NONE
        #sslctx.verify_mode = ssl.CERT_REQUIRED # doesn't work because OSError: (-30336, 'MBEDTLS_ERR_SSL_CA_CHAIN_REQUIRED') 
    except Exception:
        pass


async def ws_test_echo(session):
    async with session.ws_connect(URL, ssl=sslctx) as ws:
        await ws.send_str("hello world!\r\n")
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                print(msg.data)
            if "close" in msg.data:
                break
            await ws.send_str("close\r\n")
        await ws.close()


async def main():
    async with aiohttp.ClientSession() as session:
        await ws_test_echo(session)


if __name__ == "__main__":
    asyncio.run(main())
