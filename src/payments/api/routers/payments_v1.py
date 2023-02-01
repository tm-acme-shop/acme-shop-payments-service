"""
Payment API v1 endpoints (deprecated).

TODO(TEAM-API): Remove v1 endpoints after migration deadline Q2 2024.
"""

import logging
import warnings
from functools import wraps
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from src.payments.api.schemas.payments import CreatePaymentRequest, PaymentResponse
from src.payments.errors import PaymentDeclinedError, PaymentNotFoundError
from src.payments.services.payment_service import PaymentService

router = APIRouter()
payment_service = PaymentService()


def deprecated(message: str):
    """Mark an endpoint as deprecated."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator


@router.post("", response_model=PaymentResponse)
@deprecated("v1 API is deprecated. Use POST /api/v2/payments instead.")
def create_payment(request: CreatePaymentRequest):
    """
    Create a new payment.
    
    Deprecated: Use v2 API instead.
    """
    logging.info("Creating payment for user_id=%s, amount=%s", request.user_id, request.amount)

    try:
        payment = payment_service.create_payment(
            user_id=request.user_id,
            amount=request.amount,
            currency=request.currency,
        )
        logging.info("Payment created successfully: payment_id=%s", payment["payment_id"])
        return PaymentResponse(**payment)
    except PaymentDeclinedError as e:
        logging.error("Payment declined: %s", e.reason)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{payment_id}", response_model=PaymentResponse)
@deprecated("v1 API is deprecated. Use GET /api/v2/payments/{id} instead.")
def get_payment(payment_id: str):
    """
    Get payment details.
    
    Deprecated: Use v2 API instead.
    """
    logging.info("Getting payment: payment_id=%s", payment_id)

    try:
        payment = payment_service.get_payment(payment_id)
        return PaymentResponse(**payment)
    except PaymentNotFoundError as e:
        logging.error("Payment not found: %s", payment_id)
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
@deprecated("v1 API is deprecated. Use POST /api/v2/payments/{id}/refund instead.")
def refund_payment(payment_id: str):
    """
    Refund a payment.
    
    Deprecated: Use v2 API instead.
    """
    logging.info("Refunding payment: payment_id=%s", payment_id)

    try:
        payment = payment_service.refund_payment(payment_id)
        logging.info("Payment refunded successfully: payment_id=%s", payment_id)
        return PaymentResponse(**payment)
    except PaymentNotFoundError as e:
        logging.error("Payment not found for refund: %s", payment_id)
        raise HTTPException(status_code=404, detail=str(e))
