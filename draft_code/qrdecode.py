import qrdecode
import random

# Create a 240x240 byte buffer
buffer = bytearray(240 * 240)

# Fill buffer with random bytes

# Image dimensions
width = 240
height = 240
buffer_size = width * height  # 240 * 240 = 57600 bytes
try:
    # Allocate buffer for grayscale image
    buffer = bytearray(buffer_size)
    #for i in range(240 * 240):
    #    buffer[i] = random.getrandbits(8)
    # Read the raw grayscale image file
    with open('qrcode2.raw', 'rb') as f:
        bytes_read = f.readinto(buffer)
        if bytes_read != buffer_size:
            raise ValueError("File size does not match expected 240x240 grayscale image")
    # Decode QR code using qrdecode module
    print("decoding...")
    print(f"buffer length: {len(buffer)}")
    for i in range(15):
        print(buffer[i])
    result = qrdecode.qrdecode(buffer, width, height)
    print(f"result: {result}")
    # Remove BOM (\ufeff) from the start of the decoded string, if present
    #if result.startswith('\ufeff'):
    #    result = result[1:]
    print(f"result: {result}")
except OSError as e:
    print("Error reading file:", e)
    raise
except ValueError as e:
    print("Error:", e)
    raise
