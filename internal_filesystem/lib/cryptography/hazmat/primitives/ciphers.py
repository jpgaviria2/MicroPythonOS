# cipher.py: MicroPython compatibility layer for cryptography.hazmat.primitives.ciphers
# Implements Cipher, algorithms.AES, and modes.CBC using ucryptolib

from ucryptolib import aes

class Cipher:
    """Emulates cryptography's Cipher for AES encryption/decryption."""
    def __init__(self, algorithm, mode):
        self.algorithm = algorithm
        self.mode = mode
        self._key = algorithm.key
        self._iv = mode.iv if mode.iv is not None else b'\x00' * 16
        self._cipher = aes(self._key, 1)  # Mode 1 = CBC

    def encryptor(self):
        return Encryptor(self._cipher, self._iv)

    def decryptor(self):
        return Decryptor(self._cipher, self._iv)

class Encryptor:
    """Handles encryption with the initialized cipher."""
    def __init__(self, cipher, iv):
        self._cipher = cipher
        self._iv = iv
        self._buffer = bytearray()

    def update(self, data):
        self._buffer.extend(data)
        # MicroPython's ucryptolib processes full blocks
        block_size = 16  # AES block size
        if len(self._buffer) >= block_size:
            to_process = self._buffer[:len(self._buffer) - (len(self._buffer) % block_size)]
            self._buffer = self._buffer[len(to_process):]
            return self._cipher.encrypt(to_process)
        return b''

    def finalize(self):
        if self._buffer:
            # Pad remaining data if needed (handled by caller with PKCS7)
            return self._cipher.encrypt(self._buffer)
        return b''

class Decryptor:
    """Handles decryption with the initialized cipher."""
    def __init__(self, cipher, iv):
        self._cipher = cipher
        self._iv = iv
        self._buffer = bytearray()

    def update(self, data):
        self._buffer.extend(data)
        block_size = 16
        if len(self._buffer) >= block_size:
            to_process = self._buffer[:len(self._buffer) - (len(self._buffer) % block_size)]
            self._buffer = self._buffer[len(to_process):]
            return self._cipher.decrypt(to_process)
        return b''

    def finalize(self):
        if self._buffer:
            return self._cipher.decrypt(self._buffer)
        return b''

class algorithms:
    """Namespace for cipher algorithms."""
    class AES:
        def __init__(self, key):
            if len(key) not in (16, 24, 32):  # 128, 192, 256-bit keys
                raise ValueError("AES key must be 16, 24, or 32 bytes")
            self.key = key
            self.block_size = 128  # Bits

class modes:
    """Namespace for cipher modes."""
    class CBC:
        def __init__(self, iv):
            if len(iv) != 16:
                raise ValueError("CBC IV must be 16 bytes")
            self.iv = iv
