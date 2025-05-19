import ssl
import aiohttp
import asyncio

sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
sslctx.verify_mode = ssl.CERT_NONE
#sslctx.verify_mode = ssl.CERT_REQUIRED # doesn't work because OSError: (-30336, 'MBEDTLS_ERR_SSL_CA_CHAIN_REQUIRED') 

async def ws_test_echo(session):
    async with session.ws_connect("wss://echo.websocket.events", ssl=sslctx) as ws:
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

asyncio.run(main())
