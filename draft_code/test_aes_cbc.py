import ucryptolib
import os

key = os.urandom(32)
iv = bytes.fromhex("cafc34a94307c35f8c8f736831713467")
#iv = bytes.fromhex("cafc34a94307c35f8c8f736831713468") # changing the IV doesn't change the output!
#iv = os.urandom(16)
data = b'{"method":"get_balance","params":{}}'
pad_length = 16 - (len(data) % 16)
padded_data = data + bytes([pad_length] * pad_length)
print(f"Test padded_data: {padded_data.hex()}")

cipher = ucryptolib.aes(key, 1, iv)
ciphertext = cipher.encrypt(padded_data)
print(f"Test ciphertext: {ciphertext.hex()}")

cipher = ucryptolib.aes(key, 1, iv)
decrypted = cipher.decrypt(ciphertext)
print(f"Test decrypted: {decrypted.hex()}")

pad_length = decrypted[-1]
if decrypted[-pad_length:] != bytes([pad_length] * pad_length):
    print(f"Test failed: invalid padding, got {decrypted[-pad_length:].hex()}")
else:
    print(f"Test passed: valid padding")
