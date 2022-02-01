"""Payment API v1 endpoints."""

import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from src.payments.api.schemas.payments import CreatePaymentRequest, PaymentResponse
from src.payments.errors import PaymentDeclinedError, PaymentNotFoundError
from src.payments.services.payment_service import PaymentService

router = APIRouter()
payment_service = PaymentService()


@router.post("", response_model=PaymentResponse)
def create_payment(request: CreatePaymentRequest):
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
def get_payment(payment_id: str):
    logging.info("Getting payment: payment_id=%s", payment_id)

    try:
        payment = payment_service.get_payment(payment_id)
        return PaymentResponse(**payment)
    except PaymentNotFoundError as e:
        logging.error("Payment not found: %s", payment_id)
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(payment_id: str):
    logging.info("Refunding payment: payment_id=%s", payment_id)

    try:
        payment = payment_service.refund_payment(payment_id)
        logging.info("Payment refunded successfully: payment_id=%s", payment_id)
        return PaymentResponse(**payment)
    except PaymentNotFoundError as e:
        logging.error("Payment not found for refund: %s", payment_id)
        raise HTTPException(status_code=404, detail=str(e))
