"""Webhook payload schemas for payment providers."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class StripeEventType(str, Enum):
    """Stripe webhook event types we handle."""
    PAYMENT_INTENT_SUCCEEDED = "payment_intent.succeeded"
    PAYMENT_INTENT_FAILED = "payment_intent.payment_failed"
    PAYMENT_INTENT_CANCELLED = "payment_intent.canceled"
    CHARGE_REFUNDED = "charge.refunded"
    CHARGE_DISPUTE_CREATED = "charge.dispute.created"
    CHARGE_DISPUTE_CLOSED = "charge.dispute.closed"


class PayPalEventType(str, Enum):
    """PayPal webhook event types we handle."""
    PAYMENT_CAPTURE_COMPLETED = "PAYMENT.CAPTURE.COMPLETED"
    PAYMENT_CAPTURE_DENIED = "PAYMENT.CAPTURE.DENIED"
    PAYMENT_CAPTURE_REFUNDED = "PAYMENT.CAPTURE.REFUNDED"


class StripeWebhookPayload(BaseModel):
    """Stripe webhook event payload."""
    
    id: str = Field(..., description="Event ID")
    type: str = Field(..., description="Event type")
    api_version: str = Field(..., description="Stripe API version")
    created: int = Field(..., description="Unix timestamp")
    data: dict[str, Any] = Field(..., description="Event data")
    livemode: bool = Field(default=False)
    pending_webhooks: int = Field(default=0)
    request: Optional[dict[str, Any]] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "evt_abc123",
                "type": "payment_intent.succeeded",
                "api_version": "2023-10-16",
                "created": 1705312200,
                "data": {
                    "object": {
                        "id": "pi_xxx",
                        "amount": 9999,
                        "currency": "usd",
                        "status": "succeeded",
                    }
                },
                "livemode": False,
            }
        }
    }


class PayPalWebhookPayload(BaseModel):
    """PayPal webhook event payload."""
    
    id: str = Field(..., description="Event ID")
    event_type: str = Field(..., description="Event type")
    event_version: str = Field(default="1.0")
    create_time: str = Field(..., description="ISO 8601 timestamp")
    resource_type: str = Field(..., description="Resource type")
    resource: dict[str, Any] = Field(..., description="Event resource")
    summary: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "WH-abc123",
                "event_type": "PAYMENT.CAPTURE.COMPLETED",
                "event_version": "1.0",
                "create_time": "2024-01-15T10:30:00Z",
                "resource_type": "capture",
                "resource": {
                    "id": "CAP-xxx",
                    "amount": {"value": "99.99", "currency_code": "USD"},
                    "status": "COMPLETED",
                },
                "summary": "Payment completed",
            }
        }
    }


class WebhookResponse(BaseModel):
    """Response schema for webhook handling."""
    
    received: bool = Field(default=True)
    event_id: str
    event_type: str
    processed: bool = Field(default=True)
    message: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "received": True,
                "event_id": "evt_abc123",
                "event_type": "payment_intent.succeeded",
                "processed": True,
                "message": "Payment status updated",
            }
        }
    }


class WebhookVerificationResult(BaseModel):
    """Result of webhook signature verification."""
    
    valid: bool
    provider: str
    event_id: Optional[str] = None
    error: Optional[str] = None
    
    # TODO(TEAM-SEC): Add signature algorithm info for audit logging
