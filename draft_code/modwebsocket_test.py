import socket
import ssl
import ubinascii
from websocket import websocket
import select

# Resolve hostname
host = 'ws.postman-echo.com'
port = 443
handshake_path = '/raw'
# Option: echo.websocket.events (unreliable)
#host = 'echo.websocket.events'
#handshake_path = '/'

try:
    addr_info = socket.getaddrinfo(host, port)[0][-1]
    print('Resolved address:', addr_info)
except Exception as e:
    print('DNS resolution failed:', e)
    raise

# Create and connect socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect(addr_info)
    print('Socket connected')
except Exception as e:
    print('Connect failed:', e)
    sock.close()
    raise

# Wrap socket with SSL
try:
    ssl_sock = ssl.wrap_socket(sock, server_hostname=host)
    print('SSL connection established')
except Exception as e:
    print('SSL wrap failed:', e)
    sock.close()
    raise

# Set socket to non-blocking
ssl_sock.setblocking(False)

# Perform WebSocket handshake
key = ubinascii.b2a_base64(b'random_bytes_here').strip()
handshake = (
    'GET {} HTTP/1.1\r\n'
    'Host: {}\r\n'
    'Upgrade: websocket\r\n'
    'Connection: Upgrade\r\n'
    'Sec-WebSocket-Key: {}\r\n'
    'Sec-WebSocket-Version: 13\r\n'
    '\r\n'
).format(handshake_path, host, key.decode())

try:
    ssl_sock.write(handshake.encode())
    print('Handshake sent')
except Exception as e:
    print('Failed to send handshake:', e)
    ssl_sock.close()
    raise

# Read HTTP response until \r\n\r\n
response_bytes = bytearray()
poller = select.poll()
poller.register(ssl_sock, select.POLLIN)
max_polls = 50  # 5s timeout (50 * 100ms)
for poll_count in range(max_polls):
    if poller.poll(100):
        chunk = ssl_sock.read(128)
        if chunk is None:
            continue
        if not chunk:
            break
        response_bytes.extend(chunk)
        if b'\r\n\r\n' in response_bytes:
            http_response_bytes = response_bytes[:response_bytes.find(b'\r\n\r\n') + 4]
            try:
                response = http_response_bytes.decode('utf-8')
                if '101 Switching Protocols' not in response:
                    raise Exception('Handshake failed')
                print('Handshake successful')
                break
            except UnicodeError as e:
                print('UnicodeError:', e)
                ssl_sock.close()
                raise Exception('Failed to decode HTTP response')
    else:
        continue
else:
    ssl_sock.close()
    print('Handshake timeout: No response received after {} seconds ({} bytes received)'.format(max_polls * 0.1, len(response_bytes)))
    raise Exception('Handshake timeout')

# Create WebSocket object
ws = websocket(ssl_sock, True)
print('WebSocket object created')

# Send and receive data
ws.write('Hello, Secure WebSocket!')
max_attempts = 5
for attempt in range(max_attempts):
    if poller.poll(100):
        data = ws.read(1024)
        if data:
            print('Received:', data)
            break
    else:
        print('Read attempt', attempt + 1, 'no data')
else:
    print('Read timeout: No response received after {} attempts ({} seconds)'.format(max_attempts, max_attempts * 0.1))

# Close connection
ws.close()
print('Connection closed')
