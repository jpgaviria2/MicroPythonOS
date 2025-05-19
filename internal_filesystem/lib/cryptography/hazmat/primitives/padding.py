# primitives.py: MicroPython compatibility layer for cryptography.hazmat.primitives.padding
# Implements PKCS7 padding and unpadding

def _byte_padding_check(block_size):
    """Validate block size for padding."""
    if not (0 <= block_size <= 2040):
        raise ValueError("block_size must be in range(0, 2041).")
    if block_size % 8 != 0:
        raise ValueError("block_size must be a multiple of 8.")

class PKCS7PaddingContext:
    """Handles PKCS7 padding."""
    def __init__(self, block_size):
        _byte_padding_check(block_size)
        self.block_size = block_size // 8  # Convert bits to bytes
        self._buffer = bytearray()

    def update(self, data):
        self._buffer.extend(data)
        # Return full blocks
        block_size = self.block_size
        if len(self._buffer) >= block_size:
            to_return = self._buffer[:len(self._buffer) - (len(self._buffer) % block_size)]
            self._buffer = self._buffer[len(to_return):]
            return to_return
        return b''

    def finalize(self):
        # Pad with bytes equal to padding length
        pad_length = self.block_size - (len(self._buffer) % self.block_size)
        padding = bytes([pad_length] * pad_length)
        self._buffer.extend(padding)
        result = bytes(self._buffer)
        self._buffer = bytearray()
        return result

class PKCS7UnpaddingContext:
    """Handles PKCS7 unpadding."""
    def __init__(self, block_size):
        _byte_padding_check(block_size)
        self.block_size = block_size // 8
        self._buffer = bytearray()

    def update(self, data):
        self._buffer.extend(data)
        # Only process complete blocks
        block_size = self.block_size
        if len(self._buffer) >= block_size:
            to_return = self._buffer[:len(self._buffer) - (len(self._buffer) % block_size)]
            self._buffer = self._buffer[len(to_return):]
            return to_return
        return b''

    def finalize(self):
        if not self._buffer or len(self._buffer) % self.block_size != 0:
            raise ValueError("Invalid padding")
        pad_length = self._buffer[-1]
        if pad_length > self.block_size or pad_length == 0:
            raise ValueError("Invalid padding")
        if self._buffer[-pad_length:] != bytes([pad_length] * pad_length):
            raise ValueError("Invalid padding")
        result = bytes(self._buffer[:-pad_length])
        self._buffer = bytearray()
        return result

class PKCS7:
    """PKCS7 padding implementation."""
    def __init__(self, block_size):
        _byte_padding_check(block_size)
        self.block_size = block_size

    def padder(self):
        return PKCS7PaddingContext(self.block_size)

    def unpadder(self):
        return PKCS7UnpaddingContext(self.block_size)
