"""
PaymentClient interface definition.

This mirrors the PaymentClient interface from shared-go, providing
a consistent abstraction for payment provider integrations.

All payment providers must implement this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ChargeResult:
    """Result of a charge operation."""
    
    success: bool
    provider_transaction_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[dict[str, Any]] = None


@dataclass
class RefundResult:
    """Result of a refund operation."""
    
    success: bool
    provider_refund_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[dict[str, Any]] = None


@dataclass
class CaptureResult:
    """Result of a capture operation."""
    
    success: bool
    provider_transaction_id: Optional[str] = None
    captured_amount_cents: int = 0
    error_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class VoidResult:
    """Result of a void/cancel operation."""
    
    success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class PaymentClient(ABC):
    """
    Abstract base class for payment provider clients.
    
    This interface mirrors the PaymentClient from shared-go, ensuring
    consistent behavior across Go and Python services.
    
    All payment providers (Stripe, PayPal, etc.) must implement this interface.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'stripe', 'paypal')."""
        raise NotImplementedError
    
    @abstractmethod
    async def charge(
        self,
        *,
        amount_cents: int,
        currency: str,
        customer_id: str,
        description: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        capture: bool = True,
    ) -> ChargeResult:
        """
        Create a charge/payment intent.
        
        Args:
            amount_cents: Amount to charge in cents
            currency: ISO 4217 currency code (e.g., "USD")
            customer_id: Customer identifier
            description: Optional payment description
            metadata: Optional metadata to attach to the payment
            capture: Whether to capture immediately or authorize only
            
        Returns:
            ChargeResult with success status and provider transaction ID
        """
        raise NotImplementedError
    
    @abstractmethod
    async def capture(
        self,
        *,
        provider_transaction_id: str,
        amount_cents: Optional[int] = None,
    ) -> CaptureResult:
        """
        Capture a previously authorized payment.
        
        Args:
            provider_transaction_id: The provider's transaction/payment intent ID
            amount_cents: Optional amount for partial capture
            
        Returns:
            CaptureResult with success status
        """
        raise NotImplementedError
    
    @abstractmethod
    async def refund(
        self,
        *,
        provider_transaction_id: str,
        amount_cents: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> RefundResult:
        """
        Refund a payment.
        
        Args:
            provider_transaction_id: The provider's transaction ID to refund
            amount_cents: Optional amount for partial refund (full refund if None)
            reason: Optional refund reason
            
        Returns:
            RefundResult with success status and provider refund ID
        """
        raise NotImplementedError
    
    @abstractmethod
    async def void(
        self,
        *,
        provider_transaction_id: str,
    ) -> VoidResult:
        """
        Void/cancel a pending or authorized payment.
        
        Args:
            provider_transaction_id: The provider's transaction ID to void
            
        Returns:
            VoidResult with success status
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_transaction(
        self,
        *,
        provider_transaction_id: str,
    ) -> Optional[dict[str, Any]]:
        """
        Get transaction details from the provider.
        
        Args:
            provider_transaction_id: The provider's transaction ID
            
        Returns:
            Transaction details as dict, or None if not found
        """
        raise NotImplementedError


class LegacyPaymentClient(ABC):
    """
    Legacy payment client interface.
    
    TODO(TEAM-PAYMENTS): Remove after v1 API deprecation.
    
    This interface exists for backward compatibility with older
    payment processing code that uses synchronous methods.
    """
    
    @abstractmethod
    def process_payment_sync(
        self,
        user_id: str,
        amount: int,
        currency_code: str,
    ) -> dict[str, Any]:
        """
        Process a payment synchronously (deprecated).
        
        TODO(TEAM-PAYMENTS): Migrate to async PaymentClient.charge()
        """
        raise NotImplementedError
    
    @abstractmethod
    def process_refund_sync(
        self,
        transaction_reference: str,
        amount: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Process a refund synchronously (deprecated).
        
        TODO(TEAM-PAYMENTS): Migrate to async PaymentClient.refund()
        """
        raise NotImplementedError
