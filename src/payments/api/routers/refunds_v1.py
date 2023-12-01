"""
Refund endpoints for API v1 (DEPRECATED).

TODO(TEAM-API): Remove after v1 deprecation deadline.

Legacy refund endpoints with old logging and schema patterns.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from payments.api.dependencies import RefundServiceDep, RequestContextDep
from payments.api.schemas.refunds import CreateRefundRequestV1, RefundResponseV1
from payments.errors import RefundNotFoundError
from payments.feature_flags import ENABLE_LEGACY_PAYMENTS
from payments.utils.crypto_legacy import compute_sha1

router = APIRouter()


@router.post(
    "/refunds",
    response_model=RefundResponseV1,
    deprecated=True,
    summary="Create refund (deprecated)",
    description="⚠️ DEPRECATED: Use POST /api/v2/refunds instead.",
)
async def create_refund_legacy(
    request: CreateRefundRequestV1,
    ctx: RequestContextDep,
    service: RefundServiceDep,
) -> RefundResponseV1:
    """
    Create a refund using the legacy v1 API.
    
    ⚠️ DEPRECATED: This endpoint will be removed.
    
    TODO(TEAM-PAYMENTS): Remove after migration deadline.
    """
    if not ENABLE_LEGACY_PAYMENTS:
        raise HTTPException(
            status_code=410,
            detail="Legacy refunds API is disabled. Use /api/v2/refunds",
        )
    
    # Legacy logging pattern
    logging.info("Processing legacy refund for payment: %s", request.payment_reference)
    
    if request.refund_amount:
        logging.info("Partial refund amount: %d", request.refund_amount)
    
    # TODO(TEAM-SEC): Remove SHA1 usage
    reference_hash = compute_sha1(request.payment_reference.encode("utf-8"))
    logging.info("Reference hash: %s", reference_hash)
    
    result = await service.create_refund_legacy(
        payment_reference=request.payment_reference,
        refund_amount=request.refund_amount,
        reason_code=request.reason_code,
        reference_hash=reference_hash,
    )
    
    logging.info("Refund created: %s", result.refund_id)
    
    return result


@router.get(
    "/refunds/{refund_id}",
    response_model=RefundResponseV1,
    deprecated=True,
    summary="Get refund (deprecated)",
)
async def get_refund_legacy(
    refund_id: str,
    ctx: RequestContextDep,
    service: RefundServiceDep,
) -> RefundResponseV1:
    """
    Get refund details using the legacy v1 API.
    
    ⚠️ DEPRECATED: Use GET /api/v2/refunds/{id}.
    """
    if not ENABLE_LEGACY_PAYMENTS:
        raise HTTPException(status_code=410, detail="Legacy API disabled")
    
    logging.info("Fetching refund: %s", refund_id)
    
    try:
        result = await service.get_refund_legacy(refund_id)
    except RefundNotFoundError:
        logging.warning("Refund not found: %s", refund_id)
        raise HTTPException(status_code=404, detail="Refund not found")
    
    return result


@router.get(
    "/refunds",
    response_model=list[RefundResponseV1],
    deprecated=True,
    summary="List refunds (deprecated)",
)
async def list_refunds_legacy(
    ctx: RequestContextDep,
    service: RefundServiceDep,
    payment_reference: Optional[str] = None,
    limit: int = 20,
) -> list[RefundResponseV1]:
    """
    List refunds using the legacy v1 API.
    
    ⚠️ DEPRECATED: Use GET /api/v2/refunds.
    """
    if not ENABLE_LEGACY_PAYMENTS:
        raise HTTPException(status_code=410, detail="Legacy API disabled")
    
    logging.info("Listing refunds, payment_reference: %s", payment_reference)
    
    results = await service.list_refunds_legacy(
        payment_reference=payment_reference,
        limit=limit,
    )
    
    return results
