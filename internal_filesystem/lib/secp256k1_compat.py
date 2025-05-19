# secp256k1_compat.py: Compatibility layer for secp256k1.py to use MicroPython's usecp256k1 module
# Mimics cffi's ffi and lib objects

import usecp256k1  # Your MicroPython C module

# Constants (from libsecp256k1)
SECP256K1_CONTEXT_SIGN = 1 << 8  # 256
SECP256K1_CONTEXT_VERIFY = 1 << 9  # 512
SECP256K1_EC_COMPRESSED = 1 << 1  # 2
SECP256K1_EC_UNCOMPRESSED = 0

# Dummy ffi class to mimic cffi
class FFI:
    def new(self, type_str):
        # For 'unsigned char[74]' or 'size_t *'
        if 'unsigned char' in type_str:
            size = int(type_str.split('[')[1].rstrip(']'))
            return bytearray(size)
        elif 'size_t *' in type_str:
            return [0]  # Simulate pointer to size_t
        raise ValueError(f"Unsupported ffi type: {type_str}")

    def buffer(self, obj, size=None):
        # Return bytes from bytearray or slice
        if isinstance(obj, list):
            return bytes(obj)
        return bytes(obj[:size] if size is not None else obj)

# Dummy lib class to map to usecp256k1 functions
class Lib:
    # Constants
    SECP256K1_EC_COMPRESSED = SECP256K1_EC_COMPRESSED
    SECP256K1_EC_UNCOMPRESSED = SECP256K1_EC_UNCOMPRESSED
    SECP256K1_CONTEXT_SIGN = SECP256K1_CONTEXT_SIGN
    SECP256K1_CONTEXT_VERIFY = SECP256K1_CONTEXT_VERIFY

    def secp256k1_context_create(self, flags):
        # Context is managed by usecp256k1, return dummy object
        return object()

    def secp256k1_ecdsa_signature_serialize_der(self, ctx, output, outputlen, raw_sig):
        # Call usecp256k1_ecdsa_signature_serialize_der
        try:
            result = usecp256k1.usecp256k1_ecdsa_signature_serialize_der(raw_sig)
            if result is None:
                return 0  # Mimic libsecp256k1 failure
            # Copy result to output buffer
            output[:len(result)] = result
            outputlen[0] = len(result)
            return 1  # Mimic libsecp256k1 success
        except ValueError:
            return 0  # Handle errors like invalid signature length

# Instantiate ffi and lib
ffi = FFI()
lib = Lib()

# Feature flags (set based on your usecp256k1 module's capabilities)
HAS_RECOVERABLE = hasattr(usecp256k1, 'usecp256k1_ecdsa_sign_recoverable')
HAS_SCHNORR = hasattr(usecp256k1, 'usecp256k1_schnorrsig_sign')
HAS_ECDH = hasattr(usecp256k1, 'usecp256k1_ecdh')
HAS_EXTRAKEYS = hasattr(usecp256k1, 'usecp256k1_keypair_create')
