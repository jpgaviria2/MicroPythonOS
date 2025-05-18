import socket
import ssl
import ubinascii
from websocket import websocket

# Connect to Wi-Fi
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
ssl_sock.write(handshake.encode())
response = ssl_sock.read(1024).decode()
if '101 Switching Protocols' not in response:
    ssl_sock.close()
    raise Exception('Handshake failed: ' + response)

# Create WebSocket object
ws = websocket(ssl_sock, True)

# Send and receive data
ws.write('Hello, Secure WebSocket!')
data = ws.read(1024)
print('Received:', data)

# Close connection
ws.close()
