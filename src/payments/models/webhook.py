"""Webhook event model for tracking received webhooks."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class WebhookStatus(str, Enum):
    """Webhook processing status."""
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    IGNORED = "ignored"


class WebhookProvider(str, Enum):
    """Webhook source provider."""
    STRIPE = "stripe"
    PAYPAL = "paypal"


@dataclass
class WebhookEvent:
    """
    Webhook event record.
    
    Tracks incoming webhooks for idempotency and debugging.
    """
    
    id: str
    provider: WebhookProvider
    provider_event_id: str
    event_type: str
    status: WebhookStatus
    payload: dict[str, Any]
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        provider: WebhookProvider,
        provider_event_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> "WebhookEvent":
        """Create a new webhook event record."""
        return cls(
            id=f"wh_{uuid.uuid4().hex[:16]}",
            provider=provider,
            provider_event_id=provider_event_id,
            event_type=event_type,
            status=WebhookStatus.RECEIVED,
            payload=payload,
            created_at=datetime.utcnow(),
        )
    
    def start_processing(self) -> None:
        """Mark webhook as being processed."""
        self.status = WebhookStatus.PROCESSING
    
    def complete(self) -> None:
        """Mark webhook as processed."""
        self.status = WebhookStatus.PROCESSED
        self.processed_at = datetime.utcnow()
    
    def fail(self, error_message: str) -> None:
        """Mark webhook processing as failed."""
        self.status = WebhookStatus.FAILED
        self.error_message = error_message
        self.processed_at = datetime.utcnow()
    
    def ignore(self, reason: str) -> None:
        """Mark webhook as ignored."""
        self.status = WebhookStatus.IGNORED
        self.error_message = reason
        self.processed_at = datetime.utcnow()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "provider": self.provider.value,
            "provider_event_id": self.provider_event_id,
            "event_type": self.event_type,
            "status": self.status.value,
            "payload": self.payload,
            "error_message": self.error_message,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class WebhookRetry:
    """
    Webhook retry record for failed webhook processing.
    
    TODO(TEAM-PLATFORM): Implement retry queue processing.
    """
    
    id: str
    webhook_event_id: str
    attempt_number: int
    scheduled_at: datetime
    executed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    
    @classmethod
    def schedule(
        cls,
        webhook_event_id: str,
        attempt_number: int,
        delay_seconds: int,
    ) -> "WebhookRetry":
        """Schedule a retry attempt."""
        from datetime import timedelta
        
        return cls(
            id=f"retry_{uuid.uuid4().hex[:16]}",
            webhook_event_id=webhook_event_id,
            attempt_number=attempt_number,
            scheduled_at=datetime.utcnow() + timedelta(seconds=delay_seconds),
        )
