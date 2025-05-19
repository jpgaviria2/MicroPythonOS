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
        elif type_str == 'secp256k1_pubkey *':
            return bytearray(64)  # Placeholder for pubkey
        elif type_str == 'secp256k1_ecdsa_signature *':
            return bytearray(64)  # Placeholder for signature
        elif type_str == 'secp256k1_ecdsa_recoverable_signature *':
            return bytearray(65)  # Placeholder for recoverable signature
        elif type_str == 'secp256k1_xonly_pubkey *':
            return bytearray(32)  # Placeholder for xonly pubkey
        elif type_str == 'secp256k1_keypair *':
            return bytearray(96)  # Placeholder for keypair
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
        def decorator(func):
            return func
        return decorator

# Dummy lib class to map to usecp256k1 functions
class Lib:
    SECP256K1_EC_COMPRESSED = SECP256K1_EC_COMPRESSED
    SECP256K1_EC_UNCOMPRESSED = SECP256K1_EC_UNCOMPRESSED
    SECP256K1_CONTEXT_SIGN = SECP256K1_CONTEXT_SIGN
    SECP256K1_CONTEXT_VERIFY = SECP256K1_CONTEXT_VERIFY

    def secp256k1_context_create(self, flags):
        return object()

    def secp256k1_ec_seckey_verify(self, ctx, seckey):
        try:
            return usecp256k1.usecp256k1_ec_seckey_verify(seckey)
        except AttributeError:
            # Placeholder until usecp256k1 supports this
            raise NotImplementedError("secp256k1_ec_seckey_verify not implemented in usecp256k1")

    def secp256k1_ecdsa_signature_serialize_der(self, ctx, output, outputlen, raw_sig):
        try:
            result = usecp256k1.usecp256k1_ecdsa_signature_serialize_der(raw_sig)
            if result is None:
                return 0
            output[:len(result)] = result
            outputlen[0] = len(result)
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ecdsa_signature_parse_der(self, ctx, raw_sig, ser_sig, ser_len):
        try:
            result = usecp256k1.usecp256k1_ecdsa_signature_parse_der(ser_sig)
            if result is None:
                return 0
            raw_sig[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ecdsa_signature_serialize_compact(self, ctx, output, raw_sig):
        try:
            result = usecp256k1.usecp256k1_ecdsa_signature_serialize_compact(raw_sig)
            if result is None:
                return 0
            output[:64] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ecdsa_signature_parse_compact(self, ctx, raw_sig, ser_sig):
        try:
            result = usecp256k1.usecp256k1_ecdsa_signature_parse_compact(ser_sig)
            if result is None:
                return 0
            raw_sig[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ecdsa_signature_normalize(self, ctx, sigout, raw_sig):
        try:
            is_normalized = usecp256k1.usecp256k1_ecdsa_signature_normalize(raw_sig)
            if sigout != FFI.NULL:
                sigout[:] = is_normalized[1] if is_normalized[1] else raw_sig
            return is_normalized[0]
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ecdsa_sign(self, ctx, raw_sig, msg32, privkey, nonce_fn, nonce_data):
        try:
            result = usecp256k1.usecp256k1_ecdsa_sign(msg32, privkey)
            if result is None:
                return 0
            raw_sig[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ecdsa_verify(self, ctx, raw_sig, msg32, pubkey):
        try:
            return usecp256k1.usecp256k1_ecdsa_verify(raw_sig, msg32, pubkey)
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ecdsa_recoverable_signature_serialize_compact(self, ctx, output, recid, recover_sig):
        try:
            result, rec_id = usecp256k1.usecp256k1_ecdsa_recoverable_signature_serialize_compact(recover_sig)
            if result is None:
                return 0
            output[:64] = result
            recid[0] = rec_id
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ecdsa_recoverable_signature_parse_compact(self, ctx, recover_sig, ser_sig, rec_id):
        try:
            result = usecp256k1.usecp256k1_ecdsa_recoverable_signature_parse_compact(ser_sig, rec_id)
            if result is None:
                return 0
            recover_sig[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ecdsa_recoverable_signature_convert(self, ctx, normal_sig, recover_sig):
        try:
            result = usecp256k1.usecp256k1_ecdsa_recoverable_signature_convert(recover_sig)
            if result is None:
                return 0
            normal_sig[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ecdsa_sign_recoverable(self, ctx, raw_sig, msg32, privkey, nonce_fn, nonce_data):
        try:
            result = usecp256k1.usecp256k1_ecdsa_sign_recoverable(msg32, privkey)
            if result is None:
                return 0
            raw_sig[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ecdsa_recover(self, ctx, pubkey, recover_sig, msg32):
        try:
            result = usecp256k1.usecp256k1_ecdsa_recover(recover_sig, msg32)
            if result is None:
                return 0
            pubkey[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_schnorrsig_sign_custom(self, ctx, sig64, msg, msg_len, keypair, aux_rand32):
        try:
            result = usecp256k1.usecp256k1_schnorrsig_sign_custom(msg, keypair)
            if result is None:
                return 0
            sig64[:64] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_schnorrsig_verify(self, ctx, schnorr_sig, msg, msg_len, xonly_pubkey):
        try:
            return usecp256k1.usecp256k1_schnorrsig_verify(schnorr_sig, msg, xonly_pubkey)
        except (ValueError, AttributeError):
            return 0

    def secp256k1_tagged_sha256(self, ctx, hash32, tag, tag_len, msg, msg_len):
        try:
            result = usecp256k1.usecp256k1_tagged_sha256(tag, msg)
            if result is None:
                return 0
            hash32[:32] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ec_pubkey_serialize(self, ctx, output, outlen, pubkey, flags):
        try:
            result = usecp256k1.usecp256k1_ec_pubkey_serialize(pubkey, flags)
            if result is None:
                return 0
            output[:outlen[0]] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ec_pubkey_parse(self, ctx, pubkey, pubkey_ser, ser_len):
        try:
            result = usecp256k1.usecp256k1_ec_pubkey_parse(pubkey_ser)
            if result is None:
                return 0
            pubkey[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ec_pubkey_combine(self, ctx, outpub, pubkeys, n_pubkeys):
        try:
            result = usecp256k1.usecp256k1_ec_pubkey_combine(pubkeys)
            if result is None:
                return 0
            outpub[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ec_pubkey_tweak_add(self, ctx, pubkey, scalar):
        try:
            result = usecp256k1.usecp256k1_ec_pubkey_tweak_add(pubkey, scalar)
            if result is None:
                return 0
            pubkey[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ec_pubkey_tweak_mul(self, ctx, pubkey, scalar):
        try:
            result = usecp256k1.usecp256k1_ec_pubkey_tweak_mul(pubkey, scalar)
            if result is None:
                return 0
            pubkey[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ec_pubkey_create(self, ctx, pubkey, privkey):
        try:
            result = usecp256k1.usecp256k1_ec_pubkey_create(privkey)
            if result is None:
                return 0
            pubkey[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_xonly_pubkey_from_pubkey(self, ctx, xonly_pubkey, pk_parity, pubkey):
        try:
            result, parity = usecp256k1.usecp256k1_xonly_pubkey_from_pubkey(pubkey)
            if result is None:
                return 0
            xonly_pubkey[:] = result
            if pk_parity != FFI.NULL:
                pk_parity[0] = parity
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ec_privkey_tweak_add(self, ctx, privkey, scalar):
        try:
            result = usecp256k1.usecp256k1_ec_privkey_tweak_add(privkey, scalar)
            if result is None:
                return 0
            privkey[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_ec_privkey_tweak_mul(self, ctx, privkey, scalar):
        try:
            result = usecp256k1.usecp256k1_ec_privkey_tweak_mul(privkey, scalar)
            if result is None:
                return 0
            privkey[:] = result
            return 1
        except (ValueError, AttributeError):
            return 0

    def secp256k1_keypair_create(self, ctx, keypair, privkey):
        try:
            result = usecp256k1.usecp256k1_keypair_create(privkey)
            if result is None:
                return 0
            keypair[:] = result
            return 1
        except (ValueError, AttributeError):
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
