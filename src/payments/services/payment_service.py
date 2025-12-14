"""
Payment service for orchestrating payment operations.

This service handles the business logic for creating, capturing,
and managing payments across different providers.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from payments.api.schemas.payments import (
    PaymentProvider,
    PaymentResponse,
    PaymentResponseV1,
    PaymentStatus,
)
from payments.errors import (
    PaymentAlreadyProcessedError,
    PaymentDeclinedError,
    PaymentNotFoundError,
)
from payments.interfaces.payment_client import PaymentClient
from payments.logging_config import get_logger
from payments.models.payment import Payment, PaymentLegacy
from payments.providers.paypal_client import PayPalPaymentClient
from payments.providers.stripe_client import StripePaymentClient
from payments.services.transaction_manager import TransactionManager
from payments.utils.headers import RequestContext

logger = get_logger(__name__)


class PaymentService:
    """
    Payment orchestration service.
    
    Handles all payment-related business logic including creation,
    capture, cancellation, and retrieval.
    """
    
    def __init__(
        self,
        request_context: Optional[RequestContext] = None,
        payment_client: Optional[PaymentClient] = None,
    ):
        self._request_context = request_context
        self._payment_client = payment_client
        self._api_version = "v2"
        self._transaction_manager = TransactionManager()
        
        # In-memory storage for development
        # TODO(TEAM-PAYMENTS): Replace with database repository
        self._payments: dict[str, Payment] = {}
    
    def set_api_version(self, version: str) -> None:
        """Set the API version for response formatting."""
        self._api_version = version
    
    def _get_client(self, provider: PaymentProvider) -> PaymentClient:
        """Get payment client for provider."""
        if self._payment_client:
            return self._payment_client
        
        if provider == PaymentProvider.STRIPE:
            return StripePaymentClient()
        elif provider == PaymentProvider.PAYPAL:
            return PayPalPaymentClient()
        else:
            return StripePaymentClient()
    
    async def create_payment(
        self,
        amount_cents: int,
        currency: str,
        customer_id: str,
        order_id: str,
        provider: PaymentProvider = PaymentProvider.STRIPE,
        description: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        capture_immediately: bool = True,
    ) -> PaymentResponse:
        """
        Create a new payment.
        
        Orchestrates the payment creation through the appropriate provider.
        """
        logger.info(
            "Creating payment",
            extra={
                "customer_id": customer_id,
                "order_id": order_id,
                "amount_cents": amount_cents,
                "currency": currency,
                "provider": provider.value,
                "request_id": self._request_context.request_id if self._request_context else None,
            },
        )
        
        # Create payment model
        payment = Payment.create(
            amount_cents=amount_cents,
            currency=currency,
            customer_id=customer_id,
            order_id=order_id,
            provider=provider,
            description=description,
            metadata=metadata,
        )
        
        # Get provider client and charge
        client = self._get_client(provider)
        result = await client.charge(
            amount_cents=amount_cents,
            currency=currency,
            customer_id=customer_id,
            description=description,
            metadata=metadata,
            capture=capture_immediately,
        )
        
        if result.success:
            if capture_immediately:
                payment.capture()
            else:
                payment.authorize(result.provider_transaction_id or "")
            payment.provider_transaction_id = result.provider_transaction_id
        else:
            payment.fail()
            raise PaymentDeclinedError(
                reason=result.error_message or "Payment declined",
                decline_code=result.error_code,
                provider=provider.value,
            )
        
        # Store payment
        self._payments[payment.id] = payment
        
        logger.info(
            "Payment created successfully",
            extra={
                "payment_id": payment.id,
                "status": payment.status.value,
                "provider_transaction_id": payment.provider_transaction_id,
            },
        )
        
        return self._to_response(payment)
    
    async def get_payment(self, payment_id: str) -> PaymentResponse:
        """Get payment by ID."""
        payment = self._payments.get(payment_id)
        if not payment:
            raise PaymentNotFoundError(payment_id)
        
        return self._to_response(payment)
    
    async def capture_payment(
        self,
        payment_id: str,
        amount_cents: Optional[int] = None,
    ) -> PaymentResponse:
        """Capture an authorized payment."""
        payment = self._payments.get(payment_id)
        if not payment:
            raise PaymentNotFoundError(payment_id)
        
        if not payment.is_capturable:
            raise PaymentAlreadyProcessedError(payment_id, payment.status.value)
        
        client = self._get_client(payment.provider)
        result = await client.capture(
            provider_transaction_id=payment.provider_transaction_id or "",
            amount_cents=amount_cents,
        )
        
        if result.success:
            payment.capture(amount_cents)
        
        return self._to_response(payment)
    
    async def cancel_payment(self, payment_id: str) -> PaymentResponse:
        """Cancel a pending or authorized payment."""
        payment = self._payments.get(payment_id)
        if not payment:
            raise PaymentNotFoundError(payment_id)
        
        if payment.status not in (PaymentStatus.PENDING, PaymentStatus.AUTHORIZED):
            raise PaymentAlreadyProcessedError(payment_id, payment.status.value)
        
        client = self._get_client(payment.provider)
        await client.void(provider_transaction_id=payment.provider_transaction_id or "")
        
        payment.cancel()
        
        return self._to_response(payment)
    
    async def list_payments(
        self,
        customer_id: Optional[str] = None,
        order_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[PaymentResponse]:
        """List payments with optional filtering."""
        payments = list(self._payments.values())
        
        if customer_id:
            payments = [p for p in payments if p.customer_id == customer_id]
        if order_id:
            payments = [p for p in payments if p.order_id == order_id]
        
        # Sort by created_at descending
        payments.sort(key=lambda p: p.created_at, reverse=True)
        
        # Paginate
        payments = payments[offset:offset + limit]
        
        return [self._to_response(p) for p in payments]
    
    def _to_response(self, payment: Payment) -> PaymentResponse:
        """Convert Payment model to API response."""
        return PaymentResponse(
            id=payment.id,
            status=payment.status,
            amount_cents=payment.amount_cents,
            currency=payment.currency,
            customer_id=payment.customer_id,
            order_id=payment.order_id,
            provider=payment.provider,
            provider_transaction_id=payment.provider_transaction_id,
            captured_amount_cents=payment.captured_amount_cents,
            refunded_amount_cents=payment.refunded_amount_cents,
            metadata=payment.metadata,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )
    
    # Legacy methods for v1 API
    # TODO(TEAM-PAYMENTS): Remove after v1 deprecation
    
    async def process_payment_legacy(
        self,
        user_id: str,
        amount: int,
        currency_code: str,
        order_reference: str,
        payment_method: Optional[str] = None,
        idempotency_hash: Optional[str] = None,
        request_id: Optional[str] = None,
        legacy_user_id: Optional[str] = None,
    ) -> PaymentResponseV1:
        """
        Process payment using legacy v1 flow.
        
        TODO(TEAM-PAYMENTS): Remove after v1 deprecation.
        """
        # Legacy logging pattern
        logging.info("Legacy payment processing for user: %s", user_id)
        
        # Create payment using new system
        payment = Payment.create(
            amount_cents=amount,
            currency=currency_code,
            customer_id=user_id,
            order_id=order_reference,
            provider=PaymentProvider.STRIPE,
        )
        
        # Simulate processing
        payment.capture()
        payment.provider_transaction_id = f"ch_{idempotency_hash[:16] if idempotency_hash else 'legacy'}"
        
        self._payments[payment.id] = payment
        
        return PaymentResponseV1(
            payment_id=payment.id.replace("pay_", "PAY-").upper(),
            status_code="COMPLETED",
            amount=amount,
            currency_code=currency_code,
            user_id=user_id,
            order_reference=order_reference,
            transaction_reference=payment.provider_transaction_id,
            created=payment.created_at.isoformat(),
        )
    
    async def get_payment_legacy(self, payment_id: str) -> PaymentResponseV1:
        """
        Get payment using legacy v1 response format.
        
        TODO(TEAM-PAYMENTS): Remove after v1 deprecation.
        """
        # Handle legacy ID format
        normalized_id = payment_id.lower().replace("pay-", "pay_")
        
        payment = self._payments.get(normalized_id)
        if not payment:
            raise PaymentNotFoundError(payment_id)
        
        return PaymentResponseV1(
            payment_id=payment.id.replace("pay_", "PAY-").upper(),
            status_code=payment.status.value.upper(),
            amount=payment.amount_cents,
            currency_code=payment.currency,
            user_id=payment.customer_id,
            order_reference=payment.order_id,
            transaction_reference=payment.provider_transaction_id,
            created=payment.created_at.isoformat(),
        )
    
    async def capture_payment_legacy(
        self,
        payment_id: str,
        amount: Optional[int] = None,
    ) -> PaymentResponseV1:
        """Capture payment with legacy response."""
        normalized_id = payment_id.lower().replace("pay-", "pay_")
        
        payment = self._payments.get(normalized_id)
        if not payment:
            raise PaymentNotFoundError(payment_id)
        
        payment.capture(amount)
        
        return await self.get_payment_legacy(payment_id)
    
    async def cancel_payment_legacy(self, payment_id: str) -> PaymentResponseV1:
        """Cancel payment with legacy response."""
        normalized_id = payment_id.lower().replace("pay-", "pay_")
        
        payment = self._payments.get(normalized_id)
        if not payment:
            raise PaymentNotFoundError(payment_id)
        
        payment.cancel()
        
        return await self.get_payment_legacy(payment_id)
