import os
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_key() -> bytes:
    key_hex = os.environ.get("ENCRYPTION_KEY", "")
    return bytes.fromhex(key_hex)


def encrypt(plaintext: str) -> str:
    """AES-256-GCM encrypt. Returns hex string: nonce:ciphertext"""
    key = _get_key()
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return f"{nonce.hex()}:{ct.hex()}"


def decrypt(token: str) -> str:
    """AES-256-GCM decrypt."""
    key = _get_key()
    nonce_hex, ct_hex = token.split(":")
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(bytes.fromhex(nonce_hex), bytes.fromhex(ct_hex), None)
    return plaintext.decode()


def mask_card(card_number: str) -> str:
    """Return only last 4 digits for logging/storage."""
    cleaned = card_number.replace(" ", "").replace("-", "")
    return f"****-****-****-{cleaned[-4:]}"
