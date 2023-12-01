"""Payment domain model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentProvider(str, Enum):
    """Supported payment providers."""
    STRIPE = "stripe"
    PAYPAL = "paypal"


@dataclass
class Payment:
    """
    Payment domain model.
    
    Represents a payment in the system with all its associated data.
    """
    
    id: str
    status: PaymentStatus
    amount_cents: int
    currency: str
    customer_id: str
    order_id: str
    provider: PaymentProvider
    provider_transaction_id: Optional[str] = None
    captured_amount_cents: int = 0
    refunded_amount_cents: int = 0
    description: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        amount_cents: int,
        currency: str,
        customer_id: str,
        order_id: str,
        provider: PaymentProvider = PaymentProvider.STRIPE,
        description: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Payment":
        """Create a new payment."""
        now = datetime.utcnow()
        return cls(
            id=f"pay_{uuid.uuid4().hex[:16]}",
            status=PaymentStatus.PENDING,
            amount_cents=amount_cents,
            currency=currency.upper(),
            customer_id=customer_id,
            order_id=order_id,
            provider=provider,
            description=description,
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
        )
    
    def authorize(self, provider_transaction_id: str) -> None:
        """Mark payment as authorized."""
        self.status = PaymentStatus.AUTHORIZED
        self.provider_transaction_id = provider_transaction_id
        self.updated_at = datetime.utcnow()
    
    def capture(self, amount_cents: Optional[int] = None) -> None:
        """Capture the payment."""
        capture_amount = amount_cents or self.amount_cents
        self.captured_amount_cents = capture_amount
        self.status = PaymentStatus.CAPTURED
        self.updated_at = datetime.utcnow()
    
    def fail(self) -> None:
        """Mark payment as failed."""
        self.status = PaymentStatus.FAILED
        self.updated_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancel the payment."""
        self.status = PaymentStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def refund(self, amount_cents: int) -> None:
        """Record a refund against this payment."""
        self.refunded_amount_cents += amount_cents
        if self.refunded_amount_cents >= self.captured_amount_cents:
            self.status = PaymentStatus.REFUNDED
        else:
            self.status = PaymentStatus.PARTIALLY_REFUNDED
        self.updated_at = datetime.utcnow()
    
    @property
    def available_refund_amount(self) -> int:
        """Amount available for refund."""
        return self.captured_amount_cents - self.refunded_amount_cents
    
    @property
    def is_capturable(self) -> bool:
        """Check if payment can be captured."""
        return self.status == PaymentStatus.AUTHORIZED
    
    @property
    def is_refundable(self) -> bool:
        """Check if payment can be refunded."""
        return self.status in (
            PaymentStatus.CAPTURED,
            PaymentStatus.PARTIALLY_REFUNDED,
        ) and self.available_refund_amount > 0
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "status": self.status.value,
            "amount_cents": self.amount_cents,
            "currency": self.currency,
            "customer_id": self.customer_id,
            "order_id": self.order_id,
            "provider": self.provider.value,
            "provider_transaction_id": self.provider_transaction_id,
            "captured_amount_cents": self.captured_amount_cents,
            "refunded_amount_cents": self.refunded_amount_cents,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class PaymentLegacy:
    """
    Legacy payment model for v1 API compatibility.
    
    TODO(TEAM-PAYMENTS): Remove after v1 deprecation.
    """
    
    payment_id: str
    status_code: str
    amount: int
    currency_code: str
    user_id: str
    order_reference: str
    transaction_reference: Optional[str] = None
    created: str = ""
    
    @classmethod
    def from_payment(cls, payment: Payment) -> "PaymentLegacy":
        """Convert from modern Payment model."""
        status_map = {
            PaymentStatus.PENDING: "PENDING",
            PaymentStatus.AUTHORIZED: "AUTHORIZED",
            PaymentStatus.CAPTURED: "COMPLETED",
            PaymentStatus.FAILED: "FAILED",
            PaymentStatus.CANCELLED: "CANCELLED",
            PaymentStatus.REFUNDED: "REFUNDED",
            PaymentStatus.PARTIALLY_REFUNDED: "PARTIAL_REFUND",
        }
        
        return cls(
            payment_id=payment.id.replace("pay_", "PAY-").upper(),
            status_code=status_map.get(payment.status, "UNKNOWN"),
            amount=payment.amount_cents,
            currency_code=payment.currency,
            user_id=payment.customer_id,
            order_reference=payment.order_id.replace("ord_", "ORD-").upper(),
            transaction_reference=payment.provider_transaction_id,
            created=payment.created_at.isoformat(),
        )
