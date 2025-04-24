import usocket
import ssl
import ubinascii
import ujson
import urandom
import uhashlib
import time

subwindow.clean()
canary = lv.obj(subwindow)
canary.add_flag(lv.obj.FLAG.HIDDEN)

def compute_accept_key(key):
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    hash_obj = uhashlib.sha1(key + GUID)
    return ubinascii.b2a_base64(hash_obj.digest())[:-1].decode()

def ws_handshake(host, port, path="/"):
    print(f"Connecting to {host}:{port}")
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    addr = usocket.getaddrinfo(host, port)[0][-1]
    print(f"Resolved: {addr}")
    sock.connect(addr)

    ssl_sock = ssl.wrap_socket(sock, server_hostname=host)
    print("SSL handshake complete")

    key_bytes = bytearray()
    for _ in range(4):
        key_bytes.extend(urandom.getrandbits(32).to_bytes(4, 'big'))
    key = ubinascii.b2a_base64(key_bytes)[:-1].decode()
    expected_accept = compute_accept_key(key)
    print(f"Key: {key}")
    print(f"Expected Sec-WebSocket-Accept: {expected_accept}")

    handshake = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    )
    print(f"Handshake:\n{handshake}")
    ssl_sock.write(handshake.encode())

    response = ssl_sock.readline()
    print(f"Response: {response.decode()}")
    if b"101" not in response:
        ssl_sock.close()
        raise ValueError(f"Handshake failed: {response.decode()}")

    accept_key = None
    while True:
        line = ssl_sock.readline()
        print(f"Header: {line.decode()}")
        if line == b"\r\n":
            break
        if line.lower().startswith(b"sec-websocket-accept:"):
            accept_key = line.decode().split(":")[1].strip()

    if not accept_key:
        ssl_sock.close()
        raise ValueError("No Sec-WebSocket-Accept header received")
    if accept_key != expected_accept:
        ssl_sock.close()
        raise ValueError(f"Invalid Sec-WebSocket-Accept: got {accept_key}, expected {expected_accept}")

    # Set non-blocking read
    ssl_sock.setblocking(False)
    return ssl_sock

def ws_send_text(sock, message):
    print(f"Sending: {message}")
    data = message.encode()
    print(f"Data: {data}")
    length = len(data)

    frame = bytearray()
    frame.append(0x81)  # FIN=1, opcode=0x1 (text)
    mask_bit = 0x80
    mask_key = bytearray(urandom.getrandbits(32).to_bytes(4, 'big'))
    print(f"Mask key: {mask_key}")

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
    print(f"Frame: {frame}")
    sock.write(frame)

def ws_read_frame(sock):
    try:
        data = sock.read(2)  # Read header (FIN/opcode, length)
    except OSError as e:
        print(f"Read error: {e}")
        return None
    if not data:
        print("Read: empty")
        return None
    print(f"Raw header: {data}")

    if len(data) < 2:
        print("Frame too short")
        return None

    fin = (data[0] & 0x80) >> 7
    opcode = data[0] & 0x0F
    masked = (data[1] & 0x80) >> 7
    payload_len = data[1] & 0x7F
    print(f"FIN: {fin} Opcode: {opcode} Masked: {masked} Len: {payload_len}")

    if payload_len == 126:
        len_data = sock.read(2)
        payload_len = int.from_bytes(len_data, 'big')
        print(f"Extended len: {payload_len}")
    elif payload_len == 127:
        len_data = sock.read(8)
        payload_len = int.from_bytes(len_data, 'big')
        print(f"Extended len: {payload_len}")

    mask_key = None
    if masked:
        mask_key = sock.read(4)
        print(f"Mask key: {mask_key}")

    payload = sock.read(payload_len)
    print(f"Raw payload: {payload}")
    if masked and mask_key:
        payload = bytearray(payload)
        for i in range(len(payload)):
            payload[i] ^= mask_key[i % 4]
    print(f"Payload: {payload}")

    if opcode == 0x1:
        return payload.decode()
    elif opcode == 0x9:
        print("Ping frame received")
        return None
    elif opcode == 0xA:
        print("Pong frame received")
        return None
    elif opcode == 0x8:
        print("Close frame received")
        return None
    else:
        print(f"Unknown opcode: {opcode}")
        return None

def get_price(json_str):
    try:
        # Parse the JSON string into a Python dictionary
        data = ujson.loads(json_str)
        # Check if 'price' exists in the dictionary
        if "price" in data:
            price = data["price"]
            return price  # Return the price as a string
            # If you need it as a float, use: return float(price)
        else:
            print("Error: 'price' field not found in JSON")
            return None
    except ValueError:
        # Handle invalid JSON
        print("Error: Invalid JSON string")
        return None
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Error: An unexpected error occurred - {str(e)}")
        return None

status = lv.label(subwindow)
status.align(lv.ALIGN.TOP_LEFT, 5, 10)
status.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

summary = "Bitcoin USD price\nfrom Coinbase's Websocket API:\n\n"
status.set_text(summary)

port = 443
host = "ws-feed.exchange.coinbase.com"
path = "/"

try:
    sock = ws_handshake(host, port, path)
    print("Reading a bit...") # echo.websocket.org sends a reply
    for _ in range(3):
        time.sleep(1)
        data = ws_read_frame(sock)
        if data:
            print(f"Response: {data}")
            break
    print("Subscribing to price updates...")
    ws_send_text(sock, ujson.dumps({"type": "subscribe","product_ids": ["BTC-USD"],"channels": ["ticker_batch"]}))
    while canary.is_valid():
        time.sleep(1)            
        data = ws_read_frame(sock)
        if data:
            print(f"Response: {data}")
            price = get_price(data)
            if price:
                print(f"Price: {price}")
                summary += f"{price}\n"
                status.set_text(summary)
    sock.close()
except Exception as e:
    print(f"Error: {str(e)}")
    try:
        sock.close()
    except:
        pass


