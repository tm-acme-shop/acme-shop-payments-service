"""
Refund endpoints for API v2 (current version).

Modern refund API with structured logging and proper schemas.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException

from payments.api.dependencies import RefundServiceV2Dep, RequestContextDep
from payments.api.schemas.refunds import CreateRefundRequest, RefundResponse
from payments.errors import (
    PaymentNotFoundError,
    RefundExceedsPaymentError,
    RefundNotFoundError,
)
from payments.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/refunds",
    response_model=RefundResponse,
    status_code=201,
    summary="Create a refund",
    description="Create a full or partial refund for a payment.",
)
async def create_refund(
    request: CreateRefundRequest,
    ctx: RequestContextDep,
    service: RefundServiceV2Dep,
) -> RefundResponse:
    """
    Create a new refund.
    
    Creates a refund for the specified payment. If amount_cents is not
    provided, a full refund is issued.
    """
    logger.info(
        "Creating refund",
        extra={
            "request_id": ctx.request_id,
            "payment_id": request.payment_id,
            "amount_cents": request.amount_cents,
            "reason": request.reason.value,
        },
    )
    
    try:
        result = await service.create_refund(
            payment_id=request.payment_id,
            amount_cents=request.amount_cents,
            reason=request.reason,
            notes=request.notes,
            metadata=request.metadata or {},
        )
    except PaymentNotFoundError:
        raise HTTPException(status_code=404, detail="Payment not found")
    except RefundExceedsPaymentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    logger.info(
        "Refund created successfully",
        extra={
            "request_id": ctx.request_id,
            "refund_id": result.id,
            "payment_id": request.payment_id,
            "amount_cents": result.amount_cents,
        },
    )
    
    return result


@router.get(
    "/refunds/{refund_id}",
    response_model=RefundResponse,
    summary="Get refund details",
)
async def get_refund(
    refund_id: str,
    ctx: RequestContextDep,
    service: RefundServiceV2Dep,
) -> RefundResponse:
    """
    Get refund details by ID.
    """
    logger.info(
        "Fetching refund",
        extra={"request_id": ctx.request_id, "refund_id": refund_id},
    )
    
    try:
        result = await service.get_refund(refund_id)
    except RefundNotFoundError:
        logger.warning(
            "Refund not found",
            extra={"request_id": ctx.request_id, "refund_id": refund_id},
        )
        raise HTTPException(status_code=404, detail="Refund not found")
    
    return result


@router.get(
    "/refunds",
    response_model=list[RefundResponse],
    summary="List refunds",
)
async def list_refunds(
    ctx: RequestContextDep,
    service: RefundServiceV2Dep,
    payment_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[RefundResponse]:
    """
    List refunds with optional filtering by payment_id.
    """
    logger.info(
        "Listing refunds",
        extra={
            "request_id": ctx.request_id,
            "payment_id": payment_id,
            "limit": limit,
            "offset": offset,
        },
    )
    
    results = await service.list_refunds(
        payment_id=payment_id,
        limit=limit,
        offset=offset,
    )
    
    return results


@router.post(
    "/refunds/{refund_id}/cancel",
    response_model=RefundResponse,
    summary="Cancel a pending refund",
)
async def cancel_refund(
    refund_id: str,
    ctx: RequestContextDep,
    service: RefundServiceV2Dep,
) -> RefundResponse:
    """
    Cancel a pending refund.
    
    Only pending refunds can be cancelled.
    """
    logger.info(
        "Cancelling refund",
        extra={"request_id": ctx.request_id, "refund_id": refund_id},
    )
    
    try:
        result = await service.cancel_refund(refund_id)
    except RefundNotFoundError:
        raise HTTPException(status_code=404, detail="Refund not found")
    
    logger.info(
        "Refund cancelled",
        extra={"request_id": ctx.request_id, "refund_id": refund_id},
    )
    
    return result
