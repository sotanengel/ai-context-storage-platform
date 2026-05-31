"""SHA-256 checksum utilities."""

import hashlib


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_of_str(text: str, encoding: str = "utf-8") -> str:
    return sha256_of_bytes(text.encode(encoding))
