"""
Custom exceptions for the payments service.

This module defines domain-specific exceptions for payment processing,
provider errors, and validation failures.
"""

from typing import Any, Optional


class PaymentError(Exception):
    """Base exception for all payment-related errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "PAYMENT_ERROR",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


class PaymentNotFoundError(PaymentError):
    """Raised when a payment cannot be found."""
    
    def __init__(self, payment_id: str):
        super().__init__(
            message=f"Payment not found: {payment_id}",
            code="PAYMENT_NOT_FOUND",
            details={"payment_id": payment_id},
        )


class PaymentDeclinedError(PaymentError):
    """Raised when a payment is declined by the provider."""
    
    def __init__(
        self,
        reason: str,
        decline_code: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        super().__init__(
            message=f"Payment declined: {reason}",
            code="PAYMENT_DECLINED",
            details={
                "reason": reason,
                "decline_code": decline_code,
                "provider": provider,
            },
        )


class PaymentAlreadyProcessedError(PaymentError):
    """Raised when attempting to process an already processed payment."""
    
    def __init__(self, payment_id: str, status: str):
        super().__init__(
            message=f"Payment {payment_id} already processed with status: {status}",
            code="PAYMENT_ALREADY_PROCESSED",
            details={"payment_id": payment_id, "status": status},
        )


class RefundError(PaymentError):
    """Base exception for refund-related errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "REFUND_ERROR",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class RefundNotFoundError(RefundError):
    """Raised when a refund cannot be found."""
    
    def __init__(self, refund_id: str):
        super().__init__(
            message=f"Refund not found: {refund_id}",
            code="REFUND_NOT_FOUND",
            details={"refund_id": refund_id},
        )


class RefundExceedsPaymentError(RefundError):
    """Raised when refund amount exceeds original payment."""
    
    def __init__(
        self,
        payment_id: str,
        requested_amount: int,
        available_amount: int,
    ):
        super().__init__(
            message=f"Refund amount {requested_amount} exceeds available {available_amount}",
            code="REFUND_EXCEEDS_PAYMENT",
            details={
                "payment_id": payment_id,
                "requested_amount": requested_amount,
                "available_amount": available_amount,
            },
        )


class ProviderError(PaymentError):
    """Base exception for payment provider errors."""
    
    def __init__(
        self,
        provider: str,
        message: str,
        provider_error_code: Optional[str] = None,
    ):
        super().__init__(
            message=f"Provider error ({provider}): {message}",
            code="PROVIDER_ERROR",
            details={
                "provider": provider,
                "provider_error_code": provider_error_code,
            },
        )


class ProviderConnectionError(ProviderError):
    """Raised when connection to payment provider fails."""
    
    def __init__(self, provider: str, reason: str):
        super().__init__(
            provider=provider,
            message=f"Connection failed: {reason}",
            provider_error_code="CONNECTION_ERROR",
        )


class ProviderTimeoutError(ProviderError):
    """Raised when payment provider request times out."""
    
    def __init__(self, provider: str, timeout_seconds: float):
        super().__init__(
            provider=provider,
            message=f"Request timed out after {timeout_seconds}s",
            provider_error_code="TIMEOUT",
        )


class WebhookError(PaymentError):
    """Base exception for webhook-related errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "WEBHOOK_ERROR",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class WebhookSignatureError(WebhookError):
    """Raised when webhook signature validation fails."""
    
    def __init__(self, provider: str, reason: str):
        super().__init__(
            message=f"Webhook signature validation failed: {reason}",
            code="WEBHOOK_SIGNATURE_INVALID",
            details={"provider": provider, "reason": reason},
        )


class ValidationError(PaymentError):
    """Raised when request validation fails."""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation error on field '{field}': {message}",
            code="VALIDATION_ERROR",
            details={"field": field},
        )


class LegacyPaymentError(PaymentError):
    """
    Error for deprecated legacy payment operations.
    
    TODO(TEAM-PAYMENTS): Remove after v1 API deprecation.
    """
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="LEGACY_PAYMENT_ERROR",
            details={"deprecated": True, "migration_guide": "/docs/api-v2-migration"},
        )
