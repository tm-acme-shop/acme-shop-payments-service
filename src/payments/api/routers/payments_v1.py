"""
Payment endpoints for API v1 (DEPRECATED).

TODO(TEAM-API): Remove after v1 deprecation deadline (2024-06-01).

This module contains the legacy v1 payment endpoints that are being
phased out in favor of the v2 API. These endpoints use:
- Legacy logging patterns (logging.info with format strings)
- Legacy request/response schemas
- MD5 hashing for idempotency (insecure)
- X-Legacy-User-Id header

New integrations should use the v2 API at /api/v2/payments.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from payments.api.dependencies import PaymentServiceLegacyDep, RequestContextDep
from payments.api.schemas.payments import (
    CreatePaymentRequestV1,
    PaymentResponseV1,
)
from payments.errors import PaymentNotFoundError
from payments.feature_flags import ENABLE_LEGACY_PAYMENTS
from payments.utils.crypto_legacy import compute_md5

router = APIRouter()


@router.post(
    "/payments",
    response_model=PaymentResponseV1,
    deprecated=True,
    summary="Create payment (deprecated)",
    description="⚠️ DEPRECATED: Use POST /api/v2/payments instead.",
)
async def create_payment_legacy(
    request: CreatePaymentRequestV1,
    ctx: RequestContextDep,
    service: PaymentServiceLegacyDep,
    x_idempotency_key: Optional[str] = Header(None),
) -> PaymentResponseV1:
    """
    Create a new payment using the legacy v1 API.
    
    ⚠️ DEPRECATED: This endpoint will be removed. Migrate to /api/v2/payments.
    
    TODO(TEAM-PAYMENTS): Remove this endpoint after migration deadline.
    """
    if not ENABLE_LEGACY_PAYMENTS:
        raise HTTPException(
            status_code=410,
            detail="Legacy payments API is disabled. Use /api/v2/payments",
        )
    
    # Legacy logging pattern - TODO(TEAM-PLATFORM): Migrate to structured logging
    logging.info("Processing legacy payment for user: %s", request.user_id)
    logging.info("Amount: %d %s", request.amount, request.currency_code)
    
    # TODO(TEAM-SEC): Replace MD5 with secure hashing
    idempotency_hash = None
    if x_idempotency_key:
        idempotency_hash = compute_md5(x_idempotency_key.encode("utf-8"))
        logging.info("Idempotency hash: %s", idempotency_hash)
    
    # Process payment using legacy service method
    result = await service.process_payment_legacy(
        user_id=request.user_id,
        amount=request.amount,
        currency_code=request.currency_code,
        order_reference=request.order_reference,
        payment_method=request.payment_method,
        idempotency_hash=idempotency_hash,
        request_id=ctx.request_id,
        legacy_user_id=ctx.legacy_user_id,
    )
    
    logging.info("Payment created: %s", result.payment_id)
    
    return result


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentResponseV1,
    deprecated=True,
    summary="Get payment (deprecated)",
    description="⚠️ DEPRECATED: Use GET /api/v2/payments/{id} instead.",
)
async def get_payment_legacy(
    payment_id: str,
    ctx: RequestContextDep,
    service: PaymentServiceLegacyDep,
) -> PaymentResponseV1:
    """
    Get payment details using the legacy v1 API.
    
    ⚠️ DEPRECATED: Migrate to /api/v2/payments/{id}.
    """
    if not ENABLE_LEGACY_PAYMENTS:
        raise HTTPException(
            status_code=410,
            detail="Legacy payments API is disabled. Use /api/v2/payments",
        )
    
    # Legacy logging
    logging.info("Fetching payment: %s", payment_id)
    
    try:
        result = await service.get_payment_legacy(payment_id)
    except PaymentNotFoundError:
        logging.warning("Payment not found: %s", payment_id)
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return result


@router.post(
    "/payments/{payment_id}/capture",
    response_model=PaymentResponseV1,
    deprecated=True,
    summary="Capture payment (deprecated)",
)
async def capture_payment_legacy(
    payment_id: str,
    ctx: RequestContextDep,
    service: PaymentServiceLegacyDep,
    amount: Optional[int] = None,
) -> PaymentResponseV1:
    """
    Capture an authorized payment.
    
    ⚠️ DEPRECATED: Use POST /api/v2/payments/{id}/capture.
    """
    if not ENABLE_LEGACY_PAYMENTS:
        raise HTTPException(status_code=410, detail="Legacy API disabled")
    
    # TODO(TEAM-PAYMENTS): Remove legacy capture logic
    logging.info("Capturing payment: %s, amount: %s", payment_id, amount)
    
    try:
        result = await service.capture_payment_legacy(payment_id, amount)
    except PaymentNotFoundError:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return result


@router.post(
    "/payments/{payment_id}/cancel",
    response_model=PaymentResponseV1,
    deprecated=True,
    summary="Cancel payment (deprecated)",
)
async def cancel_payment_legacy(
    payment_id: str,
    ctx: RequestContextDep,
    service: PaymentServiceLegacyDep,
) -> PaymentResponseV1:
    """
    Cancel a pending payment.
    
    ⚠️ DEPRECATED: Use POST /api/v2/payments/{id}/cancel.
    """
    if not ENABLE_LEGACY_PAYMENTS:
        raise HTTPException(status_code=410, detail="Legacy API disabled")
    
    logging.info("Cancelling payment: %s", payment_id)
    
    try:
        result = await service.cancel_payment_legacy(payment_id)
    except PaymentNotFoundError:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return result
