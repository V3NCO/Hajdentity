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
