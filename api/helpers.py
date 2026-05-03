from Crypto.Cipher import AES
from Crypto.Hash import CMAC

def validate_uid_hex(uid: str) -> bytes:
    if not uid:
        u = ""
    u = uid.strip().lower()
    if u.startswith('0x'):
        u = u[2:]
    try:
        uid_bytes = bytes.fromhex(u)
    except Exception:
        raise ValueError("UID is not valid hex")
    if not (4 <= len(uid_bytes) <= 16):
        raise ValueError(f"UID length {len(uid_bytes)} bytes outside expected range")
    return uid_bytes

def derive_diversified_key(master_key: bytes, uid_bytes: bytes, key_no: int) -> bytes:
    if not (0 <= key_no <= 255):
        raise ValueError("key_no must be 0..255")
    pad_len = 16 - 1 - len(uid_bytes)
    if pad_len < 0:
        raise ValueError("UID too long for simple diversification")
    div_input = bytes([key_no]) + uid_bytes + b'\x00' * pad_len
    c = CMAC.new(master_key, ciphermod=AES)
    c.update(div_input)
    return c.digest()

def pkcs7_unpad(data: bytes) -> bytes:
    if len(data) == 0:
        raise ValueError("Empty plaintext")
    pad = data[-1]
    if pad < 1 or pad > 16:
        raise ValueError("Invalid PKCS7 padding")
    if data[-pad:] != bytes([pad]) * pad:
        raise ValueError("Invalid PKCS7 padding bytes")
    return data[:-pad]

def try_decrypt_p(key0: bytes, p_hex: str):
    try:
        p = bytes.fromhex(p_hex)
    except Exception:
        raise ValueError("p is not valid hex")

    if len(p) >= 17:
        iv = p[:16]
        ciphertext = p[16:]
        try:
            cipher = AES.new(key0, AES.MODE_CBC, iv)
            plaintext = cipher.decrypt(ciphertext)
            return pkcs7_unpad(plaintext)
        except Exception:
            pass

    if len(p) == 0 or len(p) % 16 != 0:
        raise ValueError("p ciphertext length invalid for AES-CBC")
    iv = b'\x00' * 16
    cipher = AES.new(key0, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(p)
    try:
        return pkcs7_unpad(plaintext)
    except Exception as e:
        raise ValueError(f"Decryption failed (padding): {e}")
