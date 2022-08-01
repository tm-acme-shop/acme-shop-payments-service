"""Payment endpoints for API v2."""

from fastapi import APIRouter, HTTPException

from src.payments.api.schemas.payments import CreatePaymentRequest, PaymentResponse
from src.payments.errors import PaymentNotFoundError
from src.payments.logging_config import get_logger
from src.payments.services.payment_service import PaymentService

router = APIRouter()
logger = get_logger(__name__)
payment_service = PaymentService()


@router.post("/payments", response_model=PaymentResponse, status_code=201)
def create_payment(request: CreatePaymentRequest):
    """Create a new payment."""
    logger.info("Creating payment", extra={"user_id": request.user_id, "amount": request.amount})
    
    payment = payment_service.create_payment(
        user_id=request.user_id,
        amount=request.amount,
        currency=request.currency,
    )
    
    logger.info("Payment created", extra={"payment_id": payment["payment_id"]})
    return PaymentResponse(**payment)


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: str):
    """Get payment details."""
    logger.info("Fetching payment", extra={"payment_id": payment_id})
    
    try:
        payment = payment_service.get_payment(payment_id)
        return PaymentResponse(**payment)
    except PaymentNotFoundError:
        logger.warning("Payment not found", extra={"payment_id": payment_id})
        raise HTTPException(status_code=404, detail="Payment not found")
