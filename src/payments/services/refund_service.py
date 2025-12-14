"""
Refund service for orchestrating refund operations.

This service handles the business logic for creating and managing refunds.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from payments.api.schemas.refunds import (
    RefundReason,
    RefundResponse,
    RefundResponseV1,
    RefundStatus,
)
from payments.errors import (
    PaymentNotFoundError,
    RefundExceedsPaymentError,
    RefundNotFoundError,
)
from payments.interfaces.payment_client import PaymentClient
from payments.logging_config import get_logger
from payments.models.refund import Refund, RefundLegacy
from payments.providers.stripe_client import StripePaymentClient
from payments.utils.headers import RequestContext

logger = get_logger(__name__)


class RefundService:
    """
    Refund orchestration service.
    
    Handles all refund-related business logic including creation,
    cancellation, and retrieval.
    """
    
    def __init__(
        self,
        request_context: Optional[RequestContext] = None,
        payment_client: Optional[PaymentClient] = None,
    ):
        self._request_context = request_context
        self._payment_client = payment_client or StripePaymentClient()
        self._api_version = "v2"
        
        # In-memory storage for development
        # TODO(TEAM-PAYMENTS): Replace with database repository
        self._refunds: dict[str, Refund] = {}
        
        # Mock payment data for testing
        self._mock_payments: dict[str, dict] = {
            "pay_demo123": {
                "id": "pay_demo123",
                "amount_cents": 10000,
                "currency": "USD",
                "refunded_amount_cents": 0,
                "provider_transaction_id": "pi_demo123",
            }
        }
    
    def set_api_version(self, version: str) -> None:
        """Set the API version for response formatting."""
        self._api_version = version
    
    async def create_refund(
        self,
        payment_id: str,
        amount_cents: Optional[int] = None,
        reason: RefundReason = RefundReason.REQUESTED_BY_CUSTOMER,
        notes: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> RefundResponse:
        """
        Create a new refund.
        
        If amount_cents is not provided, creates a full refund.
        """
        logger.info(
            "Creating refund",
            extra={
                "payment_id": payment_id,
                "amount_cents": amount_cents,
                "reason": reason.value,
                "request_id": self._request_context.request_id if self._request_context else None,
            },
        )
        
        # Get payment (mock for demo)
        payment = self._mock_payments.get(payment_id)
        if not payment:
            raise PaymentNotFoundError(payment_id)
        
        available_refund = payment["amount_cents"] - payment.get("refunded_amount_cents", 0)
        refund_amount = amount_cents or available_refund
        
        if refund_amount > available_refund:
            raise RefundExceedsPaymentError(
                payment_id=payment_id,
                requested_amount=refund_amount,
                available_amount=available_refund,
            )
        
        # Create refund model
        refund = Refund.create(
            payment_id=payment_id,
            amount_cents=refund_amount,
            currency=payment.get("currency", "USD"),
            reason=reason,
            notes=notes,
            metadata=metadata,
        )
        
        # Process refund through provider
        result = await self._payment_client.refund(
            provider_transaction_id=payment.get("provider_transaction_id", ""),
            amount_cents=refund_amount,
            reason=reason.value,
        )
        
        if result.success:
            refund.process(result.provider_refund_id or "")
            refund.complete()
            
            # Update mock payment
            payment["refunded_amount_cents"] = payment.get("refunded_amount_cents", 0) + refund_amount
        else:
            refund.fail()
        
        # Store refund
        self._refunds[refund.id] = refund
        
        logger.info(
            "Refund created successfully",
            extra={
                "refund_id": refund.id,
                "status": refund.status.value,
                "provider_refund_id": refund.provider_refund_id,
            },
        )
        
        return self._to_response(refund)
    
    async def get_refund(self, refund_id: str) -> RefundResponse:
        """Get refund by ID."""
        refund = self._refunds.get(refund_id)
        if not refund:
            raise RefundNotFoundError(refund_id)
        
        return self._to_response(refund)
    
    async def cancel_refund(self, refund_id: str) -> RefundResponse:
        """Cancel a pending refund."""
        refund = self._refunds.get(refund_id)
        if not refund:
            raise RefundNotFoundError(refund_id)
        
        if not refund.is_cancellable:
            # Can't cancel non-pending refunds
            logger.warning(
                "Cannot cancel refund",
                extra={"refund_id": refund_id, "status": refund.status.value},
            )
        
        refund.cancel()
        
        return self._to_response(refund)
    
    async def list_refunds(
        self,
        payment_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RefundResponse]:
        """List refunds with optional filtering."""
        refunds = list(self._refunds.values())
        
        if payment_id:
            refunds = [r for r in refunds if r.payment_id == payment_id]
        
        # Sort by created_at descending
        refunds.sort(key=lambda r: r.created_at, reverse=True)
        
        # Paginate
        refunds = refunds[offset:offset + limit]
        
        return [self._to_response(r) for r in refunds]
    
    def _to_response(self, refund: Refund) -> RefundResponse:
        """Convert Refund model to API response."""
        return RefundResponse(
            id=refund.id,
            payment_id=refund.payment_id,
            status=refund.status,
            amount_cents=refund.amount_cents,
            currency=refund.currency,
            reason=refund.reason,
            provider_refund_id=refund.provider_refund_id,
            notes=refund.notes,
            metadata=refund.metadata,
            created_at=refund.created_at,
            updated_at=refund.updated_at,
        )
    
    # Legacy methods for v1 API
    # TODO(TEAM-PAYMENTS): Remove after v1 deprecation
    
    async def create_refund_legacy(
        self,
        payment_reference: str,
        refund_amount: Optional[int] = None,
        reason_code: Optional[str] = None,
        reference_hash: Optional[str] = None,
    ) -> RefundResponseV1:
        """
        Create refund using legacy v1 flow.
        
        TODO(TEAM-PAYMENTS): Remove after v1 deprecation.
        """
        # Legacy logging pattern
        logging.info("Legacy refund processing for payment: %s", payment_reference)
        
        # Map legacy reason code
        reason = RefundReason.REQUESTED_BY_CUSTOMER
        if reason_code == "DUPLICATE":
            reason = RefundReason.DUPLICATE
        elif reason_code == "FRAUD":
            reason = RefundReason.FRAUDULENT
        
        # Normalize payment reference
        payment_id = payment_reference.lower().replace("pay-", "pay_")
        
        # Create refund
        refund = Refund.create(
            payment_id=payment_id,
            amount_cents=refund_amount or 10000,  # Default for demo
            currency="USD",
            reason=reason,
        )
        
        refund.process(f"re_legacy_{reference_hash[:8] if reference_hash else 'demo'}")
        refund.complete()
        
        self._refunds[refund.id] = refund
        
        return RefundResponseV1(
            refund_id=refund.id.replace("ref_", "REF-").upper(),
            payment_reference=payment_reference,
            status_code="REFUNDED",
            refund_amount=refund.amount_cents,
            currency_code=refund.currency,
            reason_code=reason_code,
            created=refund.created_at.isoformat(),
        )
    
    async def get_refund_legacy(self, refund_id: str) -> RefundResponseV1:
        """
        Get refund using legacy v1 response format.
        
        TODO(TEAM-PAYMENTS): Remove after v1 deprecation.
        """
        # Handle legacy ID format
        normalized_id = refund_id.lower().replace("ref-", "ref_")
        
        refund = self._refunds.get(normalized_id)
        if not refund:
            raise RefundNotFoundError(refund_id)
        
        return RefundResponseV1(
            refund_id=refund.id.replace("ref_", "REF-").upper(),
            payment_reference=refund.payment_id.replace("pay_", "PAY-").upper(),
            status_code=refund.status.value.upper(),
            refund_amount=refund.amount_cents,
            currency_code=refund.currency,
            reason_code=refund.reason.value.upper(),
            created=refund.created_at.isoformat(),
        )
    
    async def list_refunds_legacy(
        self,
        payment_reference: Optional[str] = None,
        limit: int = 20,
    ) -> list[RefundResponseV1]:
        """List refunds with legacy response format."""
        refunds = list(self._refunds.values())
        
        if payment_reference:
            payment_id = payment_reference.lower().replace("pay-", "pay_")
            refunds = [r for r in refunds if r.payment_id == payment_id]
        
        refunds = refunds[:limit]
        
        return [
            RefundResponseV1(
                refund_id=r.id.replace("ref_", "REF-").upper(),
                payment_reference=r.payment_id.replace("pay_", "PAY-").upper(),
                status_code=r.status.value.upper(),
                refund_amount=r.amount_cents,
                currency_code=r.currency,
                reason_code=r.reason.value.upper(),
                created=r.created_at.isoformat(),
            )
            for r in refunds
        ]
