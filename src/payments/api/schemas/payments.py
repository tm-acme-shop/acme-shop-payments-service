"""Payment request and response schemas."""

from typing import Optional

from pydantic import BaseModel


class CreatePaymentRequest(BaseModel):
    """Request schema for creating a payment."""
    
    user_id: str
    amount: int
    currency: str = "USD"


class PaymentResponse(BaseModel):
    """Response schema for payment operations."""
    
    payment_id: str
    status: str
    amount: int
    currency: str
    user_id: str
