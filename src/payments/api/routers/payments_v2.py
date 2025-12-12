"""
Payment endpoints for API v2 (current version).

This module contains the modern v2 payment API with:
- Structured logging
- Modern request/response schemas
- Proper error handling
- X-Acme-Request-ID header support
"""

from typing import Optional

from fastapi import APIRouter, HTTPException

from payments.api.dependencies import PaymentServiceV2Dep, RequestContextDep
from payments.api.schemas.payments import (
    CapturePaymentRequest,
    CreatePaymentRequest,
    PaymentResponse,
)
from payments.errors import PaymentAlreadyProcessedError, PaymentNotFoundError
from payments.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=201,
    summary="Create a payment",
    description="Create a new payment for an order.",
)
async def create_payment(
    request: CreatePaymentRequest,
    ctx: RequestContextDep,
    service: PaymentServiceV2Dep,
) -> PaymentResponse:
    """
    Create a new payment.
    
    Creates a payment intent with the specified provider (Stripe or PayPal).
    The payment can be captured immediately or authorized for later capture.
    """
    logger.info(
        "Creating payment",
        extra={
            "request_id": ctx.request_id,
            "customer_id": request.customer_id,
            "order_id": request.order_id,
            "amount_cents": request.amount_cents,
            "currency": request.currency,
            "provider": request.provider.value,
        },
    )
    
    result = await service.create_payment(
        amount_cents=request.amount_cents,
        currency=request.currency,
        customer_id=request.customer_id,
        order_id=request.order_id,
        provider=request.provider,
        description=request.description,
        metadata=request.metadata or {},
        capture_immediately=request.capture_immediately,
    )
    
    logger.info(
        "Payment created successfully",
        extra={
            "request_id": ctx.request_id,
            "payment_id": result.id,
            "status": result.status.value,
        },
    )
    
    return result


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse,
    summary="Get payment details",
)
async def get_payment(
    payment_id: str,
    ctx: RequestContextDep,
    service: PaymentServiceV2Dep,
) -> PaymentResponse:
    """
    Get payment details by ID.
    
    Returns the current status and details of a payment.
    """
    logger.info(
        "Fetching payment",
        extra={"request_id": ctx.request_id, "payment_id": payment_id},
    )
    
    try:
        result = await service.get_payment(payment_id)
    except PaymentNotFoundError:
        logger.warning(
            "Payment not found",
            extra={"request_id": ctx.request_id, "payment_id": payment_id},
        )
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return result


@router.post(
    "/payments/{payment_id}/capture",
    response_model=PaymentResponse,
    summary="Capture an authorized payment",
)
async def capture_payment(
    payment_id: str,
    request: Optional[CapturePaymentRequest],
    ctx: RequestContextDep,
    service: PaymentServiceV2Dep,
) -> PaymentResponse:
    """
    Capture an authorized payment.
    
    Optionally specify an amount for partial capture.
    """
    amount_cents = request.amount_cents if request else None
    
    logger.info(
        "Capturing payment",
        extra={
            "request_id": ctx.request_id,
            "payment_id": payment_id,
            "amount_cents": amount_cents,
        },
    )
    
    try:
        result = await service.capture_payment(payment_id, amount_cents)
    except PaymentNotFoundError:
        raise HTTPException(status_code=404, detail="Payment not found")
    except PaymentAlreadyProcessedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    logger.info(
        "Payment captured",
        extra={
            "request_id": ctx.request_id,
            "payment_id": payment_id,
            "captured_amount": result.captured_amount_cents,
        },
    )
    
    return result


@router.post(
    "/payments/{payment_id}/cancel",
    response_model=PaymentResponse,
    summary="Cancel a payment",
)
async def cancel_payment(
    payment_id: str,
    ctx: RequestContextDep,
    service: PaymentServiceV2Dep,
) -> PaymentResponse:
    """
    Cancel a pending or authorized payment.
    
    Cannot cancel payments that have already been captured.
    """
    logger.info(
        "Cancelling payment",
        extra={"request_id": ctx.request_id, "payment_id": payment_id},
    )
    
    try:
        result = await service.cancel_payment(payment_id)
    except PaymentNotFoundError:
        raise HTTPException(status_code=404, detail="Payment not found")
    except PaymentAlreadyProcessedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    logger.info(
        "Payment cancelled",
        extra={"request_id": ctx.request_id, "payment_id": payment_id},
    )
    
    return result


@router.get(
    "/payments",
    response_model=list[PaymentResponse],
    summary="List payments",
)
async def list_payments(
    ctx: RequestContextDep,
    service: PaymentServiceV2Dep,
    customer_id: Optional[str] = None,
    order_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[PaymentResponse]:
    """
    List payments with optional filtering.
    
    Filter by customer_id or order_id.
    """
    logger.info(
        "Listing payments",
        extra={
            "request_id": ctx.request_id,
            "customer_id": customer_id,
            "order_id": order_id,
            "limit": limit,
            "offset": offset,
        },
    )
    
    results = await service.list_payments(
        customer_id=customer_id,
        order_id=order_id,
        limit=limit,
        offset=offset,
    )
    
    return results
