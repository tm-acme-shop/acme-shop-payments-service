"""Refund request and response schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


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


class CreateRefundRequest(BaseModel):
    """Request schema for creating a refund (v2 API)."""
    
    payment_id: str = Field(..., description="Payment to refund")
    amount_cents: Optional[int] = Field(None, gt=0, description="Partial refund amount")
    reason: RefundReason = Field(default=RefundReason.REQUESTED_BY_CUSTOMER)
    notes: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "payment_id": "pay_abc123",
                "amount_cents": 5000,
                "reason": "requested_by_customer",
                "notes": "Customer changed their mind",
            }
        }
    }


class CreateRefundRequestV1(BaseModel):
    """
    Request schema for creating a refund (v1 API - deprecated).
    
    TODO(TEAM-API): Remove after v1 deprecation deadline.
    """
    
    # Legacy field names
    payment_reference: str = Field(..., description="Payment reference (legacy)")
    refund_amount: Optional[int] = Field(None, gt=0, description="Amount to refund (legacy)")
    reason_code: Optional[str] = Field(None, description="Reason code (legacy)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "payment_reference": "PAY-ABC123",
                "refund_amount": 5000,
                "reason_code": "CUSTOMER_REQUEST",
            }
        }
    }


class RefundResponse(BaseModel):
    """Response schema for refund operations (v2 API)."""
    
    id: str = Field(..., description="Refund identifier")
    payment_id: str
    status: RefundStatus
    amount_cents: int
    currency: str
    reason: RefundReason
    provider_refund_id: Optional[str] = None
    notes: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "ref_xyz789",
                "payment_id": "pay_abc123",
                "status": "completed",
                "amount_cents": 5000,
                "currency": "USD",
                "reason": "requested_by_customer",
                "provider_refund_id": "re_xxx",
                "created_at": "2024-01-16T14:00:00Z",
                "updated_at": "2024-01-16T14:00:05Z",
            }
        }
    }


class RefundResponseV1(BaseModel):
    """
    Response schema for refund operations (v1 API - deprecated).
    
    TODO(TEAM-API): Remove after v1 deprecation deadline.
    """
    
    # Legacy response format
    refund_id: str = Field(..., description="Refund ID (legacy)")
    payment_reference: str
    status_code: str = Field(..., description="Status code (legacy)")
    refund_amount: int
    currency_code: str
    reason_code: Optional[str] = None
    created: str  # ISO string
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "refund_id": "REF-XYZ789",
                "payment_reference": "PAY-ABC123",
                "status_code": "REFUNDED",
                "refund_amount": 5000,
                "currency_code": "USD",
                "reason_code": "CUSTOMER_REQUEST",
                "created": "2024-01-16T14:00:00Z",
            }
        }
    }
