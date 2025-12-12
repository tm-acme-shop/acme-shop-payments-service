"""Payment request and response schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


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


class CreatePaymentRequest(BaseModel):
    """Request schema for creating a payment (v2 API)."""
    
    amount_cents: int = Field(..., gt=0, description="Amount in cents")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    customer_id: str = Field(..., description="Customer identifier")
    order_id: str = Field(..., description="Order identifier")
    provider: PaymentProvider = Field(default=PaymentProvider.STRIPE)
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)
    capture_immediately: bool = Field(default=True, description="Whether to capture immediately")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "amount_cents": 9999,
                "currency": "USD",
                "customer_id": "cust_123",
                "order_id": "ord_456",
                "provider": "stripe",
                "description": "Order #456 payment",
                "capture_immediately": True,
            }
        }
    }


class CreatePaymentRequestV1(BaseModel):
    """
    Request schema for creating a payment (v1 API - deprecated).
    
    TODO(TEAM-API): Remove after v1 deprecation deadline.
    """
    
    # Legacy fields use different naming conventions
    amount: int = Field(..., gt=0, description="Amount in cents (legacy)")
    currency_code: str = Field(..., description="Currency code (legacy)")
    user_id: str = Field(..., description="User ID (legacy)")  # Was customer_id
    order_reference: str = Field(..., description="Order reference (legacy)")  # Was order_id
    payment_method: Optional[str] = Field(None, description="Payment method (legacy)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 9999,
                "currency_code": "USD",
                "user_id": "user_123",
                "order_reference": "ORD-456",
                "payment_method": "card",
            }
        }
    }


class CapturePaymentRequest(BaseModel):
    """Request schema for capturing an authorized payment."""
    
    amount_cents: Optional[int] = Field(None, gt=0, description="Amount to capture (partial)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "amount_cents": 5000,
            }
        }
    }


class PaymentResponse(BaseModel):
    """Response schema for payment operations (v2 API)."""
    
    id: str = Field(..., description="Payment identifier")
    status: PaymentStatus
    amount_cents: int
    currency: str
    customer_id: str
    order_id: str
    provider: PaymentProvider
    provider_transaction_id: Optional[str] = None
    captured_amount_cents: int = 0
    refunded_amount_cents: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "pay_abc123",
                "status": "captured",
                "amount_cents": 9999,
                "currency": "USD",
                "customer_id": "cust_123",
                "order_id": "ord_456",
                "provider": "stripe",
                "provider_transaction_id": "pi_xxx",
                "captured_amount_cents": 9999,
                "refunded_amount_cents": 0,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:05Z",
            }
        }
    }


class PaymentResponseV1(BaseModel):
    """
    Response schema for payment operations (v1 API - deprecated).
    
    TODO(TEAM-API): Remove after v1 deprecation deadline.
    """
    
    # Legacy response format
    payment_id: str = Field(..., description="Payment ID (legacy)")
    status_code: str = Field(..., description="Status code (legacy)")
    amount: int
    currency_code: str
    user_id: str
    order_reference: str
    transaction_reference: Optional[str] = None
    created: str  # ISO string instead of datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "payment_id": "PAY-ABC123",
                "status_code": "COMPLETED",
                "amount": 9999,
                "currency_code": "USD",
                "user_id": "user_123",
                "order_reference": "ORD-456",
                "transaction_reference": "TXN-XXX",
                "created": "2024-01-15T10:30:00Z",
            }
        }
    }
