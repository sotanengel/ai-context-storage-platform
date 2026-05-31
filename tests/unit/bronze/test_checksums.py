"""Tests for SHA-256 checksum utilities."""

from formaforge.bronze.checksums import sha256_of_bytes, sha256_of_str


def test_sha256_of_bytes_known_value() -> None:
    result = sha256_of_bytes(b"hello")
    assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_sha256_of_str_known_value() -> None:
    result = sha256_of_str("hello")
    assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_sha256_of_bytes_empty() -> None:
    result = sha256_of_bytes(b"")
    assert result == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_sha256_of_bytes_is_hex() -> None:
    result = sha256_of_bytes(b"test")
    assert all(c in "0123456789abcdef" for c in result)
    assert len(result) == 64


def test_sha256_deterministic() -> None:
    data = b"deterministic input"
    assert sha256_of_bytes(data) == sha256_of_bytes(data)
