import socket
import ssl
import ubinascii
from websocket import websocket
import time

# Connect to Wi-Fi (disabled as per your code)
if False:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('your_ssid', 'your_password')
    while not wlan.isconnected():
        pass
    print('Connected:', wlan.ifconfig())

# Resolve hostname
# Option 1: echo.websocket.events (unreliable)
host = 'echo.websocket.events'
port = 443
handshake_path = '/'
# Option 2: ws.postman-echo.com (recommended for testing)
# host = 'ws.postman-echo.com'
# port = 443
# handshake_path = '/raw'

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
print('Socket set to non-blocking')

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

# Send handshake request
try:
    bytes_written = ssl_sock.write(handshake.encode())
    print('Handshake sent, bytes written:', bytes_written)
    print('Handshake request:', handshake)
except Exception as e:
    print('Failed to send handshake:', e)
    ssl_sock.close()
    raise

# Read HTTP response until \r\n\r\n (minimize reading)
response_bytes = bytearray()
max_read = 1024
read_timeout = 2
start_time = time.time()
while len(response_bytes) < max_read:
    try:
        chunk = ssl_sock.read(128)
        if not chunk:
            print('No more data received (EOF)')
            break
        print('Received chunk, length:', len(chunk), 'bytes:', chunk)
        response_bytes.extend(chunk)
        print('Total bytes received:', len(response_bytes))
        if b'\r\n\r\n' in response_bytes:
            print('End of HTTP headers detected')
            # Decode and verify HTTP response immediately
            http_end = response_bytes.find(b'\r\n\r\n') + 4
            if http_end < 4:
                ssl_sock.close()
                raise Exception('Invalid HTTP response: no headers found')
            http_response_bytes = response_bytes[:http_end]
            try:
                response = http_response_bytes.decode('utf-8')
                print('Decoded HTTP response:', response)
            except UnicodeError as e:
                print('UnicodeError during decode:', e)
                printable = ''.join(c if 32 <= ord(c) < 127 else '.' for c in http_response_bytes.decode('latin-1'))
                print('Printable characters:', printable)
                ssl_sock.close()
                raise Exception('Failed to decode HTTP response')
            if '101 Switching Protocols' not in response:
                print('Handshake response:', response)
                ssl_sock.close()
                raise Exception('Handshake failed')
            # Stop reading to leave WebSocket frame in socket buffer
            print('Stopping read to preserve WebSocket frame')
            break
    except Exception as e:
        print('Error reading chunk:', e)
        break
    if time.time() - start_time > read_timeout:
        print('Read timeout reached')
        break

# Create WebSocket object
try:
    ws = websocket(ssl_sock, True)
    print('WebSocket object created')
except Exception as e:
    print('Failed to create WebSocket object:', e)
    ssl_sock.close()
    raise

# Send and receive data with retries
try:
    bytes_written = ws.write('Hello, Secure WebSocket!')
    print('Sent message, bytes written:', bytes_written)
except Exception as e:
    print('Failed to send message:', e)
    ws.close()
    raise

# Try reading multiple times to catch initial message or echo
max_attempts = 5
read_timeout = 1  # Short timeout per read
for attempt in range(max_attempts):
    try:
        data = ws.read(1024)
        print('Read attempt', attempt + 1, 'received:', data)
        if data:
            break
        time.sleep(0.5)  # Wait briefly before retrying
    except Exception as e:
        print('Read attempt', attempt + 1, 'error:', e)
        time.sleep(0.5)
    if time.time() - start_time > read_timeout:
        print('Read timeout reached')
        break

# Close connection
ws.close()
print('Connection closed')
