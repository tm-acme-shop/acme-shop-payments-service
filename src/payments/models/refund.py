"""Refund domain model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class RefundStatus(str, Enum):
    """Refund status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefundReason(str, Enum):
    """Refund reason enumeration."""
    DUPLICATE = "duplicate"
    FRAUDULENT = "fraudulent"
    REQUESTED_BY_CUSTOMER = "requested_by_customer"
    ORDER_CANCELLED = "order_cancelled"
    PRODUCT_NOT_RECEIVED = "product_not_received"
    PRODUCT_UNACCEPTABLE = "product_unacceptable"
    OTHER = "other"


@dataclass
class Refund:
    """
    Refund domain model.
    
    Represents a refund against a payment.
    """
    
    id: str
    payment_id: str
    status: RefundStatus
    amount_cents: int
    currency: str
    reason: RefundReason
    provider_refund_id: Optional[str] = None
    notes: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        payment_id: str,
        amount_cents: int,
        currency: str,
        reason: RefundReason = RefundReason.REQUESTED_BY_CUSTOMER,
        notes: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Refund":
        """Create a new refund."""
        now = datetime.utcnow()
        return cls(
            id=f"ref_{uuid.uuid4().hex[:16]}",
            payment_id=payment_id,
            status=RefundStatus.PENDING,
            amount_cents=amount_cents,
            currency=currency.upper(),
            reason=reason,
            notes=notes,
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
        )
    
    def process(self, provider_refund_id: str) -> None:
        """Mark refund as processing."""
        self.status = RefundStatus.PROCESSING
        self.provider_refund_id = provider_refund_id
        self.updated_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark refund as completed."""
        self.status = RefundStatus.COMPLETED
        self.updated_at = datetime.utcnow()
    
    def fail(self) -> None:
        """Mark refund as failed."""
        self.status = RefundStatus.FAILED
        self.updated_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancel the refund."""
        self.status = RefundStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    @property
    def is_cancellable(self) -> bool:
        """Check if refund can be cancelled."""
        return self.status == RefundStatus.PENDING
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "payment_id": self.payment_id,
            "status": self.status.value,
            "amount_cents": self.amount_cents,
            "currency": self.currency,
            "reason": self.reason.value,
            "provider_refund_id": self.provider_refund_id,
            "notes": self.notes,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class RefundLegacy:
    """
    Legacy refund model for v1 API compatibility.
    
    TODO(TEAM-PAYMENTS): Remove after v1 deprecation.
    """
    
    refund_id: str
    payment_reference: str
    status_code: str
    refund_amount: int
    currency_code: str
    reason_code: Optional[str] = None
    created: str = ""
    
    @classmethod
    def from_refund(cls, refund: Refund) -> "RefundLegacy":
        """Convert from modern Refund model."""
        status_map = {
            RefundStatus.PENDING: "PENDING",
            RefundStatus.PROCESSING: "PROCESSING",
            RefundStatus.COMPLETED: "REFUNDED",
            RefundStatus.FAILED: "FAILED",
            RefundStatus.CANCELLED: "CANCELLED",
        }
        
        reason_map = {
            RefundReason.DUPLICATE: "DUPLICATE",
            RefundReason.FRAUDULENT: "FRAUD",
            RefundReason.REQUESTED_BY_CUSTOMER: "CUSTOMER_REQUEST",
            RefundReason.ORDER_CANCELLED: "ORDER_CANCEL",
            RefundReason.PRODUCT_NOT_RECEIVED: "NOT_RECEIVED",
            RefundReason.PRODUCT_UNACCEPTABLE: "UNACCEPTABLE",
            RefundReason.OTHER: "OTHER",
        }
        
        return cls(
            refund_id=refund.id.replace("ref_", "REF-").upper(),
            payment_reference=refund.payment_id.replace("pay_", "PAY-").upper(),
            status_code=status_map.get(refund.status, "UNKNOWN"),
            refund_amount=refund.amount_cents,
            currency_code=refund.currency,
            reason_code=reason_map.get(refund.reason),
            created=refund.created_at.isoformat(),
        )
