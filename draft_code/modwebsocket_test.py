import socket
import ssl
import ubinascii
from websocket import websocket

# Connect to Wi-Fi (disabled as per your code)
if False:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('your_ssid', 'your_password')
    while not wlan.isconnected():
        pass
    print('Connected:', wlan.ifconfig())

# Resolve hostname
host = 'echo.websocket.events'  # Replace with your WSS server
port = 443
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

# Perform WebSocket handshake
key = ubinascii.b2a_base64(b'random_bytes_here').strip()
handshake = (
    'GET / HTTP/1.1\r\n'
    'Host: {}\r\n'
    'Upgrade: websocket\r\n'
    'Connection: Upgrade\r\n'
    'Sec-WebSocket-Key: {}\r\n'
    'Sec-WebSocket-Version: 13\r\n'
    '\r\n'
).format(host, key.decode())

# Send handshake request
try:
    bytes_written = ssl_sock.write(handshake.encode())
    print('Handshake sent, bytes written:', bytes_written)
    print('Handshake request:', handshake)
except Exception as e:
    print('Failed to send handshake:', e)
    ssl_sock.close()
    raise

# Read response in chunks with debugging
response_bytes = bytearray()
max_read = 1024  # Maximum bytes to read
read_timeout = 10  # Timeout in seconds (adjust as needed)
import time

start_time = time.time()
while len(response_bytes) < max_read:
    try:
        # Read a small chunk to avoid blocking too long
        chunk = ssl_sock.read(128)
        if not chunk:  # EOF or connection closed
            print('No more data received (EOF)')
            break
        print('Received chunk, length:', len(chunk), 'bytes:', chunk)
        response_bytes.extend(chunk)
        print('Total bytes received:', len(response_bytes))
    except Exception as e:
        print('Error reading chunk:', e)
        break
    if time.time() - start_time > read_timeout:
        print('Read timeout reached')
        break

# Inspect raw bytes
print('Raw response bytes:', response_bytes)
print('Raw response hex:', response_bytes.hex())

# Attempt to decode response
try:
    response = response_bytes.decode('utf-8')
    print('Decoded response:', response)
except UnicodeError as e:
    print('UnicodeError during decode:', e)
    # Try decoding with 'ignore' to see partial response
    response = response_bytes.decode('utf-8', errors='ignore')
    print('Decoded with errors ignored:', response)
    # Try alternative encoding (e.g., latin-1)
    try:
        response = response_bytes.decode('latin-1')
        print('Decoded as latin-1:', response)
    except Exception as e:
        print('Latin-1 decode failed:', e)
    # Dump printable characters
    printable = ''.join(c if 32 <= ord(c) < 127 else '.' for c in response_bytes.decode('latin-1'))
    print('Printable characters:', printable)
    ssl_sock.close()
    raise Exception('Failed to decode response')

# Check for valid WebSocket handshake
if '101 Switching Protocols' not in response:
    print('Handshake response:', response)
    ssl_sock.close()
    raise Exception('Handshake failed')

# Create WebSocket object
ws = websocket(ssl_sock, True)

# Send and receive data
ws.write('Hello, Secure WebSocket!')
data = ws.read(1024)
print('Received:', data)

# Close connection
ws.close()
