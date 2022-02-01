"""Payment service for handling payment operations."""

import logging
from typing import Any, Dict
from uuid import uuid4


class PaymentService:
    """Service for managing payments."""
    
    def __init__(self):
        self._payments: Dict[str, Dict[str, Any]] = {}
    
    def create_payment(self, user_id: str, amount: int, currency: str) -> Dict[str, Any]:
        """Create a new payment."""
        payment_id = f"pay_{uuid4().hex[:16]}"
        
        payment = {
            "payment_id": payment_id,
            "status": "completed",
            "amount": amount,
            "currency": currency,
            "user_id": user_id,
        }
        
        self._payments[payment_id] = payment
        logging.info("Payment stored: %s", payment_id)
        
        return payment
    
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """Get payment by ID."""
        from src.payments.errors import PaymentNotFoundError
        
        payment = self._payments.get(payment_id)
        if not payment:
            raise PaymentNotFoundError(payment_id)
        
        return payment
    
    def refund_payment(self, payment_id: str) -> Dict[str, Any]:
        """Refund a payment."""
        from src.payments.errors import PaymentNotFoundError
        
        payment = self._payments.get(payment_id)
        if not payment:
            raise PaymentNotFoundError(payment_id)
        
        payment["status"] = "refunded"
        logging.info("Payment refunded: %s", payment_id)
        
        return payment
