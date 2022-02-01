"""Payment service errors."""


class PaymentError(Exception):
    """Base payment error."""
    pass


class PaymentNotFoundError(PaymentError):
    """Payment not found."""
    
    def __init__(self, payment_id: str):
        self.payment_id = payment_id
        super().__init__(f"Payment not found: {payment_id}")


class PaymentDeclinedError(PaymentError):
    """Payment was declined."""
    
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Payment declined: {reason}")
