"""Transaction domain model for tracking payment operations."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class TransactionType(str, Enum):
    """Types of transactions."""
    AUTHORIZATION = "authorization"
    CAPTURE = "capture"
    REFUND = "refund"
    VOID = "void"


class TransactionStatus(str, Enum):
    """Transaction status."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Transaction:
    """
    Transaction record for audit trail.
    
    Tracks individual operations (auth, capture, refund) against payments.
    """
    
    id: str
    payment_id: str
    type: TransactionType
    status: TransactionStatus
    amount_cents: int
    currency: str
    provider: str
    provider_transaction_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        payment_id: str,
        transaction_type: TransactionType,
        amount_cents: int,
        currency: str,
        provider: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Transaction":
        """Create a new transaction record."""
        return cls(
            id=f"txn_{uuid.uuid4().hex[:16]}",
            payment_id=payment_id,
            type=transaction_type,
            status=TransactionStatus.PENDING,
            amount_cents=amount_cents,
            currency=currency.upper(),
            provider=provider,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )
    
    def succeed(self, provider_transaction_id: str) -> None:
        """Mark transaction as successful."""
        self.status = TransactionStatus.SUCCESS
        self.provider_transaction_id = provider_transaction_id
    
    def fail(self, error_code: str, error_message: str) -> None:
        """Mark transaction as failed."""
        self.status = TransactionStatus.FAILED
        self.error_code = error_code
        self.error_message = error_message
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "payment_id": self.payment_id,
            "type": self.type.value,
            "status": self.status.value,
            "amount_cents": self.amount_cents,
            "currency": self.currency,
            "provider": self.provider,
            "provider_transaction_id": self.provider_transaction_id,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class TransactionLog:
    """
    Immutable transaction log entry for compliance.
    
    TODO(TEAM-PAYMENTS): Add encryption for sensitive fields.
    """
    
    id: str
    transaction_id: str
    event: str
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def log_event(
        cls,
        transaction_id: str,
        event: str,
        data: Optional[dict[str, Any]] = None,
    ) -> "TransactionLog":
        """Create a log entry."""
        return cls(
            id=f"log_{uuid.uuid4().hex[:16]}",
            transaction_id=transaction_id,
            event=event,
            data=data or {},
            timestamp=datetime.utcnow(),
        )
