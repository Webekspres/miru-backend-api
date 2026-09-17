"""
Field-level encryption service for sensitive data (NIK, KTP data at-rest).

Uses Fernet symmetric encryption with Django's SECRET_KEY as the base key.
Fernet guarantees that encrypted data cannot be tampered with or read
without the key.
"""

import base64
import hashlib

from django.conf import settings
from cryptography.fernet import Fernet


def _get_fernet() -> Fernet:
    """
    Derive a 32-byte URL-safe base64 key from Django's SECRET_KEY.

    This ensures that:
    - The encryption key is unique per installation (different SECRET_KEY
      means different encryption key).
    - We don't need to store a separate encryption key in the environment.
    - Fernet's 128-bit AES in CBC mode with HMAC authentication.
    """
    raw = hashlib.sha256(settings.SECRET_KEY.encode('utf-8')).digest()
    key = base64.urlsafe_b64encode(raw)
    return Fernet(key)


def encrypt_value(plaintext: str) -> str:
    """Encrypt a plaintext string. Returns a base64-encoded ciphertext string."""
    if not plaintext:
        return ''
    f = _get_fernet()
    ciphertext = f.encrypt(plaintext.encode('utf-8'))
    return ciphertext.decode('utf-8')


def decrypt_value(ciphertext: str) -> str:
    """Decrypt a ciphertext string back to plaintext."""
    if not ciphertext:
        return ''
    f = _get_fernet()
    plaintext = f.decrypt(ciphertext.encode('utf-8'))
    return plaintext.decode('utf-8')
