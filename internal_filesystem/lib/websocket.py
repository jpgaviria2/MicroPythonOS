# websocket.py
# MicroPython WebSocketApp implementation for python-nostr port
# Compatible with websocket-client's WebSocketApp API, using MicroPython aiohttp

import uasyncio as asyncio
import time
import ucollections
import aiohttp
from aiohttp import WSMsgType, ClientWebSocketResponse

# Simplified logging for MicroPython
def _log_debug(msg):
    print(f"DEBUG: {msg}")

def _log_error(msg):
    print(f"ERROR: {msg}")

# Simplified ABNF for opcode compatibility
class ABNF:
    OPCODE_TEXT = 1
    OPCODE_BINARY = 2
    OPCODE_CLOSE = 8
    OPCODE_PING = 9
    OPCODE_PONG = 10

# Exceptions
class WebSocketException(Exception):
    pass

class WebSocketConnectionClosedException(WebSocketException):
    pass

class WebSocketTimeoutException(WebSocketException):
    pass

# Queue for callback dispatching (in same thread)
_callback_queue = ucollections.deque((), 100)  # Empty tuple, maxlen=100

def _run_callback(callback, *args):
    """Add callback to queue for execution."""
    try:
        _callback_queue.append((callback, args))
    except IndexError:
        _log_error("Callback queue full, dropping callback")

def _process_callbacks():
    """Process queued callbacks."""
    while _callback_queue:
        print("processing callbacks queue...")
        try:
            callback, args = _callback_queue.popleft()
            if callback is not None:
                try:
                    callback(*args)
                except Exception as e:
                    _log_error(f"Error in callback {callback}: {e}")
            else:
                print("Not calling None callback")
        except IndexError:
            break  # Queue is empty

class WebSocketApp:
    def __init__(
        self,
        url,
        header=None,
        on_open=None,
        on_reconnect=None,
        on_message=None,
        on_error=None,
        on_close=None,
        on_ping=None,
        on_pong=None,
        on_cont_message=None,
        keep_running=True,  # Ignored for compatibility
        get_mask_key=None,
        cookie=None,
        subprotocols=None,
        on_data=None,
        socket=None,
    ):
        self.url = url
        self.header = header if header is not None else {}
        self.cookie = cookie
        self.on_open = on_open
        self.on_reconnect = on_reconnect
        self.on_message = on_message
        self.on_data = on_data
        self.on_error = on_error
        self.on_close = on_close
        self.on_ping = on_ping
        self.on_pong = on_pong
        self.on_cont_message = on_cont_message
        self.get_mask_key = get_mask_key
        self.subprotocols = subprotocols
        self.prepared_socket = socket  # Ignored, not supported
        self.ws = None
        self.session = None
        self.running = False
        self.ping_interval = 0
        self.ping_timeout = None
        self.ping_payload = ""
        self.last_ping_tm = 0
        self.last_pong_tm = 0
        self.has_errored = False
        self._loop = asyncio.get_event_loop()

    def send(self, data, opcode=ABNF.OPCODE_TEXT):
        """Send a message."""
        if not self.ws or not self.running:
            raise WebSocketConnectionClosedException("Connection is already closed.")
        asyncio.create_task(self._send_async(data, opcode))

    def send_text(self, text_data):
        """Send UTF-8 text."""
        self.send(text_data, ABNF.OPCODE_TEXT)

    def send_bytes(self, data):
        """Send binary data."""
        self.send(data, ABNF.OPCODE_BINARY)

    def close(self, **kwargs):
        """Close the WebSocket connection."""
        self.running = False
        asyncio.create_task(self._close_async())

    async def _close_async(self):
        """Async close implementation."""
        try:
            if self.ws and not self.ws.ws.closed:
                await self.ws.close()
            if self.session:
                await self.session.__aexit__(None, None, None)
        except Exception as e:
            _log_error(f"Error closing WebSocket: {e}")

    def _start_ping_thread(self):
        """Start ping task."""
        if self.ping_interval:
            asyncio.create_task(self._send_ping_async())

    def _stop_ping_thread(self):
        """No-op, ping handled in async loop."""
        pass

    async def _send_ping_async(self):
        """Send periodic pings."""
        while self.running and self.ping_interval:
            self.last_ping_tm = time.time()
            try:
                
                #await self.ws.send_bytes(self.ping_payload.encode() if isinstance(self.ping_payload, str) else self.ping_payload)
                _log_debug("NOT Sending ping because it seems corrupt")
            except Exception as e:
                _log_debug(f"Failed to send ping: {e}")
            await asyncio.sleep(self.ping_interval)

    def ready(self):
        """Check if connection is active."""
        return self.ws is not None and self.running

    def run_forever(
        self,
        sockopt=None,
        sslopt=None,
        ping_interval=0,
        ping_timeout=None,
        ping_payload="",
        http_proxy_host=None,
        http_proxy_port=None,
        http_no_proxy=None,
        http_proxy_auth=None,
        http_proxy_timeout=None,
        skip_utf8_validation=False,
        host=None,
        origin=None,
        dispatcher=None,
        suppress_origin=False,
        proxy_type=None,
        reconnect=None,
    ):
        """Run the WebSocket event loop in the main thread."""
        if sockopt or http_proxy_host or http_proxy_port or http_no_proxy or http_proxy_auth or proxy_type:
            raise WebSocketException("Proxy and sockopt not supported in MicroPython")
        if dispatcher:
            raise WebSocketException("Custom dispatcher not supported")
        if ping_timeout is not None and ping_timeout <= 0:
            raise WebSocketException("Ensure ping_timeout > 0")
        if ping_interval is not None and ping_interval < 0:
            raise WebSocketException("Ensure ping_interval >= 0")
        if ping_timeout and ping_interval and ping_interval <= ping_timeout:
            raise WebSocketException("Ensure ping_interval > ping_timeout")

        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.ping_payload = ping_payload
        self.running = True

        # Run the event loop in the main thread
        try:
            self._loop.run_until_complete(self._async_main())
        except KeyboardInterrupt:
            print("run_forever got KeyboardInterrupt")
            self.close()
            return False
        except Exception as e:
            _log_error(f"run_forever got general exception: {e} - returning True")
            self.has_errored = True
            return True
        return self.has_errored

    async def _async_main(self):
        """Main async loop for WebSocket handling."""
        reconnect = 0  # Default, as RECONNECT may not be defined
        try:
            from websocket import RECONNECT
            reconnect = RECONNECT
        except ImportError:
            pass
        if reconnect is not None:
            reconnect = reconnect

        while self.running:
            print("self.running")
            time.sleep(1)
            try:
                await self._connect_and_run()
            except Exception as e:
                _log_error(f"_async_main got exception: {e}")
                self.has_errored = True
                _run_callback(self.on_error, self, e)
                if not reconnect:
                    break
                _log_debug(f"Reconnecting after error: {e}")
                await asyncio.sleep(reconnect)
                if self.on_reconnect:
                    _run_callback(self.on_reconnect, self)

        # Cleanup
        self.running = False
        _log_debug("websocket.py: closing...")
        await self._close_async()
        _run_callback(self.on_close, self, None, None)

    async def _connect_and_run(self):
        """Connect and handle WebSocket messages."""
        ssl_context = None
        if self.url.startswith("wss://"):
            import ssl
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.verify_mode = ssl.CERT_NONE

        self.session = aiohttp.ClientSession(headers=self.header)
        async with self.session.ws_connect(self.url, ssl=ssl_context) as ws:
            self.ws = ws
            print("running on_open callback...")
            _run_callback(self.on_open, self)
            print("done running on_open callback.")
            self._start_ping_thread()

            async for msg in ws:
                print(f"websocket.py received msg: type {msg.type} - {msg.data[0:20]}")
                if not self.running:
                    break

                # Handle ping/pong timeout
                if self.ping_timeout and self.last_ping_tm:
                    if time.time() - self.last_ping_tm > self.ping_timeout:
                        raise WebSocketTimeoutException("ping/pong timed out")

                # Process message
                _process_callbacks()  # Process callbacks in same thread
                if msg.type == WSMsgType.TEXT:
                    data = msg.data
                    _run_callback(self.on_data, self, data, ABNF.OPCODE_TEXT, True)
                    _run_callback(self.on_message, self, data)
                elif msg.type == WSMsgType.BINARY:
                    data = msg.data
                    _run_callback(self.on_data, self, data, ABNF.OPCODE_BINARY, True)
                    _run_callback(self.on_message, self, data)
                elif msg.type == WSMsgType.ERROR or ws.ws.closed:
                    raise WebSocketConnectionClosedException("WebSocket closed")

    async def _send_async(self, data, opcode):
        """Async send implementation."""
        try:
            if opcode == ABNF.OPCODE_TEXT:
                await self.ws.send_str(data)
            elif opcode == ABNF.OPCODE_BINARY:
                await self.ws.send_bytes(data)
            else:
                raise WebSocketException(f"Unsupported opcode: {opcode}")
        except Exception as e:
            _run_callback(self.on_error, self, e)

    def _callback(self, callback, *args):
        """Compatibility wrapper for callback execution."""
        _run_callback(callback, self, *args)

    def _get_close_args(self, close_frame):
        """Extract close code and reason (simplified)."""
        return [None, None]  # aiohttp doesn't provide close frame details

    def create_dispatcher(self, ping_timeout, dispatcher, is_ssl, handleDisconnect):
        """Not supported."""
        raise WebSocketException("Custom dispatcher not supported")
