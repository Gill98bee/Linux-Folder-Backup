"""Encryption helpers using cryptography (AES-GCM)."""

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
from pathlib import Path
import getpass


class Passphrase:
    def __init__(self, key: bytes):
        self.key = key

    @staticmethod
    def derive_from_passphrase(passphrase: str, salt: bytes | None = None) -> bytes:
        if salt is None:
            salt = os.urandom(16)
        kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
        key = kdf.derive(passphrase.encode())
        return salt + key

    @classmethod
    def from_passphrase(cls, passphrase: str):
        raw = cls.derive_from_passphrase(passphrase)
        return cls(raw)

    @classmethod
    def prompt_if_needed(cls, env: str | None = None):
        # If env provided and set return it
        if env:
            return cls.from_passphrase(env)
        pw = getpass.getpass("Passphrase (leave empty for no encryption): ")
        if not pw:
            return None
        return cls.from_passphrase(pw)

    def encrypt_file(self, source: Path, dest: Path):
        with source.open("rb") as fh:
            data = fh.read()
        # first 16 bytes are salt
        salt = self.key[:16]
        key = self.key[16:]
        aes = AESGCM(key)
        nonce = os.urandom(12)
        ct = aes.encrypt(nonce, data, None)
        with dest.open("wb") as fh:
            fh.write(salt + nonce + ct)

    def decrypt_file(self, source: Path, dest: Path):
        with source.open("rb") as fh:
            content = fh.read()
        salt = content[:16]
        nonce = content[16:28]
        ct = content[28:]
        # derive key again from salt + stored kdf? Here we stored key after salt.
        key = self.key[16:]
        aes = AESGCM(key)
        pt = aes.decrypt(nonce, ct, None)
        with dest.open("wb") as fh:
            fh.write(pt)
