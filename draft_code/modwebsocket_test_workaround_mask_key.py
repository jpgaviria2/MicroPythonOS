import socket
import ssl
import ubinascii
from websocket import websocket
import select
import urandom

# Function to send a masked WebSocket text frame
def ws_send_text(sock, message):
    data = message.encode()
    length = len(data)

    frame = bytearray()
    frame.append(0x81)  # FIN=1, opcode=0x1 (text)
    mask_bit = 0x80
    mask_key = bytearray(urandom.getrandbits(32).to_bytes(4, 'big'))

    if length <= 125:
        frame.append(mask_bit | length)
    elif length <= 65535:
        frame.append(mask_bit | 126)
        frame.extend(length.to_bytes(2, 'big'))
    else:
        frame.append(mask_bit | 127)
        frame.extend(length.to_bytes(8, 'big'))

    frame.extend(mask_key)
    masked_data = bytearray(data)
    for i in range(len(data)):
        masked_data[i] ^= mask_key[i % 4]
    frame.extend(masked_data)
    return sock.write(frame)

# Resolve hostname
host = 'echo.websocket.events'
port = 443
handshake_path = '/'  # Matches aiohttp example
# Fallback: ws.postman-echo.com
host = 'ws.postman-echo.com'
handshake_path = '/raw'

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
    print('SSL cipher:', ssl_sock.cipher())
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
    bytes_written = ssl_sock.write(handshake.encode())
    print('Handshake sent, bytes written:', bytes_written)
except Exception as e:
    print('Failed to send handshake:', e)
    ssl_sock.close()
    raise

# Read HTTP response until \r\n\r\n
response_bytes = bytearray()
poller = select.poll()
poller.register(ssl_sock, select.POLLIN)
max_polls = 100  # 10s timeout (100 * 100ms)
for poll_count in range(max_polls):
    events = poller.poll(100)
    print('Poll', poll_count + 1, 'events:', events)
    if events:
        chunk = ssl_sock.read(128)
        if chunk is None:
            print('Read returned None, continuing')
            continue
        if not chunk:
            print('No more data received (EOF)')
            break
        response_bytes.extend(chunk)
        print('Received chunk, length:', len(chunk))
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
        print('Poll', poll_count + 1, 'no data')
else:
    ssl_sock.close()
    print('Handshake timeout: No response received after {} seconds ({} bytes received)'.format(max_polls * 0.1, len(response_bytes)))
    raise Exception('Handshake timeout')

# Create WebSocket object
ws = websocket(ssl_sock, True)
print('WebSocket object created')

# Send and receive data
try:
    # This doesn't work because the websocket module fails to set the mask bit
    # and apply a random 4-byte mask key as required by the WebSocket protocol
    # for client-to-server frames, causing the server to close the connection
    # with an "incorrect mask flag" error (status code 1002).
    # bytes_written = ws.write('hello world!\r\n')
    # print('Sent message, bytes written:', bytes_written)

    # Proper, working code using manual frame masking
    bytes_written = ws_send_text(ssl_sock, 'hello world!\r\n')
    print('Sent message, bytes written:', bytes_written)
except Exception as e:
    print('Failed to send message:', e)
    ws.close()
    raise

# Debug: Read raw socket data
try:
    events = poller.poll(500)
    if events:
        raw_data = ssl_sock.read(1024)
        print('Raw socket data:', raw_data)
        if raw_data:
            print('Raw socket data hex:', raw_data.hex())
    else:
        print('No raw socket data available')
except Exception as e:
    print('Raw socket read error:', e)

# Read WebSocket messages
max_attempts = 5  # Reduced to 5 attempts (2.5s with 500ms polls)
for attempt in range(max_attempts):
    events = poller.poll(500)
    print('Read poll attempt', attempt + 1, 'events:', events)
    if events:
        try:
            data = ws.read(1024)
            if data is None:
                print('Read attempt', attempt + 1, 'returned None')
                continue
            print('Read attempt', attempt + 1, 'received:', data)
            if data:
                continue  # Keep reading for more messages
        except Exception as e:
            print('Read attempt', attempt + 1, 'error:', e)
    else:
        print('Read attempt', attempt + 1, 'no data')
else:
    print('Read timeout: No response received after {} attempts ({} seconds)'.format(max_attempts, max_attempts * 0.5))

# Send close message
try:
    # This doesn't work because the websocket module fails to set the mask bit
    # and apply a random 4-byte mask key as required by the WebSocket protocol
    # for client-to-server frames, causing the server to close the connection
    # with an "incorrect mask flag" error (status code 1002).
    # bytes_written = ws.write('close\r\n')
    # print('Sent close, bytes written:', bytes_written)

    # Proper, working code using manual frame masking
    bytes_written = ws_send_text(ssl_sock, 'close\r\n')
    print('Sent close, bytes written:', bytes_written)
except Exception as e:
    print('Failed to send close:', e)

# Close connection
ws.close()
print('Connection closed')
