# secp256k1_compat.py: Compatibility layer for secp256k1.py to use MicroPython's usecp256k1 module

import usecp256k1

# Constants (from libsecp256k1)
SECP256K1_CONTEXT_SIGN = 1 << 8  # 256
SECP256K1_CONTEXT_VERIFY = 1 << 9  # 512
SECP256K1_EC_COMPRESSED = 1 << 1  # 2
SECP256K1_EC_UNCOMPRESSED = 0

# Dummy ffi class to mimic cffi
class FFI:
    NULL = None  # Mimic cffi's NULL pointer

    def new(self, type_str):
        if 'char' in type_str:
            size = int(type_str.split('[')[1].rstrip(']'))
            return bytearray(size)
        elif 'size_t *' in type_str:
            return [0]
        raise ValueError(f"Unsupported ffi type: {type_str}")

    def buffer(self, obj, size=None):
        if isinstance(obj, list):
            return bytes(obj)
        return bytes(obj[:size] if size is not None else obj)

    def memmove(self, dst, src, n):
        if isinstance(src, bytes):
            src = bytearray(src)
        dst[:n] = src[:n]

    def callback(self, signature):
        # Simplified decorator to mark functions without setting attributes
        def decorator(func):
            return func  # Return func as-is
        return decorator

# Dummy lib class to map to usecp256k1 functions
class Lib:
    SECP256K1_EC_COMPRESSED = SECP256K1_EC_COMPRESSED
    SECP256K1_EC_UNCOMPRESSED = SECP256K1_EC_UNCOMPRESSED
    SECP256K1_CONTEXT_SIGN = SECP256K1_CONTEXT_SIGN
    SECP256K1_CONTEXT_VERIFY = SECP256K1_CONTEXT_VERIFY

    def secp256k1_context_create(self, flags):
        return object()

    def secp256k1_ecdsa_signature_serialize_der(self, ctx, output, outputlen, raw_sig):
        try:
            result = usecp256k1.usecp256k1_ecdsa_signature_serialize_der(raw_sig)
            if result is None:
                return 0
            output[:len(result)] = result
            outputlen[0] = len(result)
            return 1
        except ValueError:
            return 0

    def secp256k1_ecdh(self, ctx, output, pubkey, seckey, hashfn=FFI.NULL, hasharg=FFI.NULL):
        try:
            result = usecp256k1.usecp256k1_ecdh(pubkey, seckey)
            if result is None:
                return 0
            output[:32] = result
            return 1
        except ValueError:
            return 0

# Instantiate ffi and lib
ffi = FFI()
lib = Lib()

# Feature flags
HAS_RECOVERABLE = hasattr(usecp256k1, 'usecp256k1_ecdsa_sign_recoverable')
HAS_SCHNORR = hasattr(usecp256k1, 'usecp256k1_schnorrsig_sign')
HAS_ECDH = hasattr(usecp256k1, 'usecp256k1_ecdh')
HAS_EXTRAKEYS = hasattr(usecp256k1, 'usecp256k1_keypair_create')

# Define copy_x for ECDH
def copy_x(output, x32, y32, data):
    ffi.memmove(output, x32, 32)
    return 1
