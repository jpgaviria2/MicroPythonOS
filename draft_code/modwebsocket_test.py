#import network
import socket
import ubinascii
from websocket import websocket


# Create and connect socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect(('echo.websocket.org', 80))
sock.connect(socket.getaddrinfo('echo.websocket.org', 80)[0][-1])
#getaddrinfo('localhost', 5000)[0][-1]

# Perform WebSocket handshake
key = ubinascii.b2a_base64(b'random_bytes_here').strip()
handshake = (
    'GET / HTTP/1.1\r\n'
    'Host: echo.websocket.org\r\n'
    'Upgrade: websocket\r\n'
    'Connection: Upgrade\r\n'
    'Sec-WebSocket-Key: {}\r\n'
    'Sec-WebSocket-Version: 13\r\n'
    '\r\n'
).format(key.decode())
sock.send(handshake.encode())
response = sock.recv(1024).decode()
print(f"reponse: {response}")
if '101 Switching Protocols' not in response:
    raise Exception('Handshake failed')

# Create WebSocket object
ws = websocket(sock, True)

# Send and receive data
ws.write('Hello, WebSocket!')
data = ws.read(1024)
print('Received:', data)

# Close connection
ws.close()
