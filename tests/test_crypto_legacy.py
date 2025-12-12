"""Tests for legacy crypto utilities."""

import pytest

from payments.utils.crypto_legacy import (
    compute_md5,
    compute_sha1,
    compute_sha256,
    verify_hmac_sha256,
    verify_hmac_md5,
    generate_idempotency_key,
)


def test_compute_md5_string() -> None:
    """Test MD5 hash of string input."""
    result = compute_md5("hello")
    assert result == "5d41402abc4b2a76b9719d911017c592"
    assert len(result) == 32


def test_compute_md5_bytes() -> None:
    """Test MD5 hash of bytes input."""
    result = compute_md5(b"hello")
    assert result == "5d41402abc4b2a76b9719d911017c592"


def test_compute_sha1_string() -> None:
    """Test SHA1 hash of string input."""
    result = compute_sha1("hello")
    assert result == "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
    assert len(result) == 40


def test_compute_sha1_bytes() -> None:
    """Test SHA1 hash of bytes input."""
    result = compute_sha1(b"hello")
    assert result == "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"


def test_compute_sha256() -> None:
    """Test SHA256 hash."""
    result = compute_sha256("hello")
    assert len(result) == 64
    assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_verify_hmac_sha256_valid() -> None:
    """Test HMAC-SHA256 verification with valid signature."""
    data = b"test data"
    secret = "secret_key"
    
    # Compute expected signature
    import hmac
    import hashlib
    expected = hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()
    
    assert verify_hmac_sha256(data, secret, expected) is True


def test_verify_hmac_sha256_invalid() -> None:
    """Test HMAC-SHA256 verification with invalid signature."""
    data = b"test data"
    secret = "secret_key"
    
    assert verify_hmac_sha256(data, secret, "invalid_signature") is False


def test_verify_hmac_md5() -> None:
    """Test legacy HMAC-MD5 verification."""
    data = b"test data"
    secret = "secret_key"
    
    import hmac
    import hashlib
    expected = hmac.new(secret.encode(), data, hashlib.md5).hexdigest()
    
    assert verify_hmac_md5(data, secret, expected) is True


def test_generate_idempotency_key() -> None:
    """Test idempotency key generation."""
    key1 = generate_idempotency_key("user123", "order456", 9999)
    key2 = generate_idempotency_key("user123", "order456", 9999)
    key3 = generate_idempotency_key("user123", "order789", 9999)
    
    # Same inputs should produce same key
    assert key1 == key2
    # Different inputs should produce different key
    assert key1 != key3
    # Key should be valid MD5 hash (32 hex chars)
    assert len(key1) == 32
