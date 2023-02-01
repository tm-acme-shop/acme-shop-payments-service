"""
Payment endpoints for API v2 (current version).

This module contains the modern v2 payment API with:
- Structured logging
- Modern request/response schemas
- Proper error handling
"""

from fastapi import APIRouter, HTTPException

from src.payments.api.schemas.payments import CreatePaymentRequest, PaymentResponse
from src.payments.errors import PaymentNotFoundError
from src.payments.logging_config import get_logger
from src.payments.services.payment_service import PaymentService

router = APIRouter()
logger = get_logger(__name__)
payment_service = PaymentService()


@router.post("/payments", response_model=PaymentResponse, status_code=201, summary="Create a payment")
def create_payment(request: CreatePaymentRequest):
    """Create a new payment."""
    logger.info(
        "Creating payment",
        extra={
            "user_id": request.user_id,
            "amount": request.amount,
            "currency": request.currency,
        },
    )
    
    payment = payment_service.create_payment(
        user_id=request.user_id,
        amount=request.amount,
        currency=request.currency,
    )
    
    logger.info("Payment created", extra={"payment_id": payment["payment_id"], "status": payment["status"]})
    return PaymentResponse(**payment)


@router.get("/payments/{payment_id}", response_model=PaymentResponse, summary="Get payment details")
def get_payment(payment_id: str):
    """Get payment details by ID."""
    logger.info("Fetching payment", extra={"payment_id": payment_id})
    
    try:
        payment = payment_service.get_payment(payment_id)
        return PaymentResponse(**payment)
    except PaymentNotFoundError:
        logger.warning("Payment not found", extra={"payment_id": payment_id})
        raise HTTPException(status_code=404, detail="Payment not found")


@router.post("/payments/{payment_id}/refund", response_model=PaymentResponse, summary="Refund a payment")
def refund_payment(payment_id: str):
    """Refund a payment."""
    logger.info("Refunding payment", extra={"payment_id": payment_id})
    
    try:
        payment = payment_service.refund_payment(payment_id)
        logger.info("Payment refunded", extra={"payment_id": payment_id})
        return PaymentResponse(**payment)
    except PaymentNotFoundError:
        logger.warning("Payment not found for refund", extra={"payment_id": payment_id})
        raise HTTPException(status_code=404, detail="Payment not found")
