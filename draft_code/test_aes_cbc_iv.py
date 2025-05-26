import ucryptolib
import os
import sys

print(f"MicroPython version: {sys.version}")
print(f"Platform: {sys.platform}")

key = os.urandom(32)
iv1 = bytes.fromhex("cafc34a94307c35f8c8f736831713467")
iv2 = bytes.fromhex("cafc34a94307c35f8c8f736831713468")
iv3 = os.urandom(16)  # Random IV
data = b'{"method":"get_balance","params":{}}'
pad_length = 16 - (len(data) % 16)
padded_data = data + bytes([pad_length] * pad_length)
print(f"Test key: {key.hex()}")
print(f"Test padded_data: {padded_data.hex()} (length: {len(padded_data)})")

mode_cbc = 2

# Test with IV1
cipher1 = ucryptolib.aes(key, mode_cbc, iv1)
ciphertext1 = cipher1.encrypt(padded_data)
print(f"IV1: {iv1.hex()}, Ciphertext1: {ciphertext1.hex()}")

# Test with IV2
cipher2 = ucryptolib.aes(key, mode_cbc, iv2)
ciphertext2 = cipher2.encrypt(padded_data)
print(f"IV2: {iv2.hex()}, Ciphertext2: {ciphertext2.hex()}")

# Test with IV3
cipher3 = ucryptolib.aes(key, mode_cbc, iv3)
ciphertext3 = cipher3.encrypt(padded_data)
print(f"IV3: {iv3.hex()}, Ciphertext3: {ciphertext3.hex()}")

# Compare ciphertexts
print(f"Ciphertext1 == Ciphertext2: {ciphertext1 == ciphertext2}")
print(f"Ciphertext1 == Ciphertext3: {ciphertext1 == ciphertext3}")

# Verify decryption
cipher_decrypt = ucryptolib.aes(key, 1, iv1)
decrypted = cipher_decrypt.decrypt(ciphertext1)
print(f"Decrypted with IV1: {decrypted.hex()}")
if decrypted[-pad_length:] != bytes([pad_length] * pad_length):
    print(f"Test failed: invalid padding, got {decrypted[-pad_length:].hex()}")
else:
    print(f"Test passed: valid padding")
