"""
Validation utilities for payment data.

Provides validation functions for payment-related data including
currency codes, amounts, and identifiers.
"""

import re
from typing import Optional

from payments.errors import ValidationError


# ISO 4217 currency codes (common subset)
VALID_CURRENCY_CODES = {
    "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD",
    "SEK", "KRW", "SGD", "NOK", "MXN", "INR", "RUB", "ZAR", "TRY", "BRL",
}

# Regex patterns for ID validation
PAYMENT_ID_PATTERN = re.compile(r"^pay_[a-f0-9]{16}$")
LEGACY_PAYMENT_ID_PATTERN = re.compile(r"^PAY-[A-F0-9]{16}$")
REFUND_ID_PATTERN = re.compile(r"^ref_[a-f0-9]{16}$")
LEGACY_REFUND_ID_PATTERN = re.compile(r"^REF-[A-F0-9]{16}$")


def validate_currency_code(currency: str) -> str:
    """
    Validate and normalize a currency code.
    
    Args:
        currency: ISO 4217 currency code
        
    Returns:
        Normalized (uppercase) currency code
        
    Raises:
        ValidationError: If currency code is invalid
    """
    normalized = currency.upper().strip()
    
    if len(normalized) != 3:
        raise ValidationError("currency", "Currency code must be 3 characters")
    
    if not normalized.isalpha():
        raise ValidationError("currency", "Currency code must be alphabetic")
    
    if normalized not in VALID_CURRENCY_CODES:
        # Warning but allow - might be a valid code we don't have in our list
        pass
    
    return normalized


def validate_amount(
    amount_cents: int,
    min_amount: int = 1,
    max_amount: int = 99999999,
) -> int:
    """
    Validate a payment amount in cents.
    
    Args:
        amount_cents: Amount in cents
        min_amount: Minimum allowed amount (default 1 cent)
        max_amount: Maximum allowed amount (default ~$1M)
        
    Returns:
        Validated amount
        
    Raises:
        ValidationError: If amount is invalid
    """
    if not isinstance(amount_cents, int):
        raise ValidationError("amount_cents", "Amount must be an integer")
    
    if amount_cents < min_amount:
        raise ValidationError("amount_cents", f"Amount must be at least {min_amount}")
    
    if amount_cents > max_amount:
        raise ValidationError("amount_cents", f"Amount cannot exceed {max_amount}")
    
    return amount_cents


def validate_payment_id(payment_id: str) -> str:
    """
    Validate a payment ID format.
    
    Accepts both modern (pay_xxx) and legacy (PAY-XXX) formats.
    
    Args:
        payment_id: Payment identifier
        
    Returns:
        Validated payment ID
        
    Raises:
        ValidationError: If payment ID format is invalid
    """
    if not payment_id:
        raise ValidationError("payment_id", "Payment ID is required")
    
    if PAYMENT_ID_PATTERN.match(payment_id):
        return payment_id
    
    # TODO(TEAM-API): Remove legacy format support after v1 deprecation
    if LEGACY_PAYMENT_ID_PATTERN.match(payment_id):
        return payment_id
    
    raise ValidationError(
        "payment_id",
        "Invalid payment ID format. Expected pay_xxx or PAY-XXX",
    )


def validate_refund_id(refund_id: str) -> str:
    """
    Validate a refund ID format.
    
    Args:
        refund_id: Refund identifier
        
    Returns:
        Validated refund ID
        
    Raises:
        ValidationError: If refund ID format is invalid
    """
    if not refund_id:
        raise ValidationError("refund_id", "Refund ID is required")
    
    if REFUND_ID_PATTERN.match(refund_id):
        return refund_id
    
    # TODO(TEAM-API): Remove legacy format support after v1 deprecation
    if LEGACY_REFUND_ID_PATTERN.match(refund_id):
        return refund_id
    
    raise ValidationError(
        "refund_id",
        "Invalid refund ID format. Expected ref_xxx or REF-XXX",
    )


def validate_customer_id(customer_id: str) -> str:
    """
    Validate a customer ID.
    
    Args:
        customer_id: Customer identifier
        
    Returns:
        Validated customer ID
        
    Raises:
        ValidationError: If customer ID is invalid
    """
    if not customer_id:
        raise ValidationError("customer_id", "Customer ID is required")
    
    if len(customer_id) > 255:
        raise ValidationError("customer_id", "Customer ID too long (max 255)")
    
    return customer_id.strip()


def validate_order_id(order_id: str) -> str:
    """
    Validate an order ID.
    
    Args:
        order_id: Order identifier
        
    Returns:
        Validated order ID
        
    Raises:
        ValidationError: If order ID is invalid
    """
    if not order_id:
        raise ValidationError("order_id", "Order ID is required")
    
    if len(order_id) > 255:
        raise ValidationError("order_id", "Order ID too long (max 255)")
    
    return order_id.strip()


def normalize_legacy_id(legacy_id: str, prefix: str = "pay") -> str:
    """
    Normalize a legacy ID to modern format.
    
    Converts PAY-ABC123 to pay_abc123.
    
    TODO(TEAM-API): Remove after v1 deprecation.
    
    Args:
        legacy_id: Legacy format ID (e.g., PAY-ABC123)
        prefix: Expected prefix (pay, ref, etc.)
        
    Returns:
        Normalized ID in modern format
    """
    upper_prefix = prefix.upper()
    
    if legacy_id.startswith(f"{upper_prefix}-"):
        # Convert PAY-ABC123 to pay_abc123
        suffix = legacy_id[len(upper_prefix) + 1:].lower()
        return f"{prefix}_{suffix}"
    
    return legacy_id
