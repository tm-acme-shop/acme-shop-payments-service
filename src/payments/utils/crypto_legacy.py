"""
Legacy cryptographic utilities.

⚠️ WARNING: This module contains INSECURE hashing functions that are
kept only for backward compatibility with legacy systems.

TODO(TEAM-SEC): Replace all MD5/SHA1 usage with secure alternatives.
"""

import hashlib
import hmac
from typing import Union


def compute_md5(data: Union[str, bytes]) -> str:
    """
    Compute MD5 hash of data.
    
    ⚠️ DEPRECATED: MD5 is cryptographically broken and should not be used
    for security-sensitive operations.
    
    TODO(TEAM-SEC): Replace with SHA-256 or better. Kept for legacy compatibility only.
    
    Args:
        data: Data to hash (string or bytes)
        
    Returns:
        Hexadecimal hash string
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    
    return hashlib.md5(data).hexdigest()


def compute_sha1(data: Union[str, bytes]) -> str:
    """
    Compute SHA1 hash of data.
    
    ⚠️ DEPRECATED: SHA1 is cryptographically weak and should not be used
    for security-sensitive operations.
    
    TODO(TEAM-SEC): Replace with SHA-256 or better. Kept for legacy compatibility only.
    
    Args:
        data: Data to hash (string or bytes)
        
    Returns:
        Hexadecimal hash string
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    
    return hashlib.sha1(data).hexdigest()


def compute_sha256(data: Union[str, bytes]) -> str:
    """
    Compute SHA256 hash of data.
    
    This is the recommended hash function for new code.
    
    Args:
        data: Data to hash (string or bytes)
        
    Returns:
        Hexadecimal hash string
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    
    return hashlib.sha256(data).hexdigest()


def verify_hmac_sha256(
    data: bytes,
    secret: str,
    expected_signature: str,
) -> bool:
    """
    Verify HMAC-SHA256 signature.
    
    Uses constant-time comparison to prevent timing attacks.
    
    Args:
        data: Data that was signed
        secret: Secret key used for signing
        expected_signature: Expected signature to verify against
        
    Returns:
        True if signature is valid, False otherwise
    """
    computed = hmac.new(
        secret.encode("utf-8"),
        data,
        hashlib.sha256,
    ).hexdigest()
    
    return hmac.compare_digest(computed, expected_signature)


def verify_hmac_md5(
    data: bytes,
    secret: str,
    expected_signature: str,
) -> bool:
    """
    Verify HMAC-MD5 signature.
    
    ⚠️ DEPRECATED: MD5 is cryptographically broken.
    
    TODO(TEAM-SEC): Migrate to HMAC-SHA256. Kept for legacy webhook validation.
    
    Args:
        data: Data that was signed
        secret: Secret key used for signing
        expected_signature: Expected signature to verify against
        
    Returns:
        True if signature is valid, False otherwise
    """
    computed = hmac.new(
        secret.encode("utf-8"),
        data,
        hashlib.md5,
    ).hexdigest()
    
    return hmac.compare_digest(computed, expected_signature)


def generate_idempotency_key(
    user_id: str,
    order_id: str,
    amount_cents: int,
) -> str:
    """
    Generate an idempotency key for payment requests.
    
    TODO(TEAM-SEC): This uses MD5 which is insecure. Migrate to SHA-256.
    
    Args:
        user_id: Customer/user identifier
        order_id: Order identifier
        amount_cents: Payment amount in cents
        
    Returns:
        Idempotency key string
    """
    # Legacy implementation using MD5
    # TODO(TEAM-SEC): Replace MD5 with SHA-256
    data = f"{user_id}:{order_id}:{amount_cents}"
    return compute_md5(data)


def hash_card_fingerprint(last_four: str, exp_month: int, exp_year: int) -> str:
    """
    Create a fingerprint hash for a card.
    
    ⚠️ DEPRECATED: Uses SHA1 which is weak.
    
    TODO(TEAM-SEC): Replace with SHA-256 and add salt.
    
    Args:
        last_four: Last 4 digits of card number
        exp_month: Expiration month
        exp_year: Expiration year
        
    Returns:
        Card fingerprint hash
    """
    data = f"{last_four}:{exp_month:02d}:{exp_year}"
    return compute_sha1(data)


class LegacyCryptoHelper:
    """
    Legacy crypto helper class.
    
    TODO(TEAM-SEC): Remove this class after full migration to secure crypto.
    
    This class provides methods that were used in the v1 API.
    """
    
    @staticmethod
    def hash_payment_reference(reference: str) -> str:
        """
        Hash a payment reference for storage.
        
        TODO(TEAM-SEC): Uses MD5 - migrate to bcrypt or Argon2.
        """
        return compute_md5(reference)
    
    @staticmethod
    def verify_webhook_signature_legacy(
        payload: bytes,
        signature: str,
        secret: str,
    ) -> bool:
        """
        Verify webhook signature using legacy MD5 method.
        
        TODO(TEAM-SEC): Migrate to HMAC-SHA256.
        """
        return verify_hmac_md5(payload, secret, signature)
