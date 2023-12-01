"""Tests for domain models."""

import pytest
from datetime import datetime

from payments.models.payment import Payment, PaymentStatus, PaymentProvider
from payments.models.refund import Refund, RefundStatus, RefundReason


class TestPaymentModel:
    """Tests for the Payment model."""
    
    def test_create_payment(self) -> None:
        """Test creating a new payment."""
        payment = Payment.create(
            amount_cents=9999,
            currency="usd",
            customer_id="cust_123",
            order_id="ord_456",
            provider=PaymentProvider.STRIPE,
            description="Test payment",
        )
        
        assert payment.id.startswith("pay_")
        assert payment.status == PaymentStatus.PENDING
        assert payment.amount_cents == 9999
        assert payment.currency == "USD"  # Normalized to uppercase
        assert payment.customer_id == "cust_123"
        assert payment.order_id == "ord_456"
        assert payment.captured_amount_cents == 0
        assert payment.refunded_amount_cents == 0
    
    def test_authorize_payment(self) -> None:
        """Test authorizing a payment."""
        payment = Payment.create(
            amount_cents=5000,
            currency="USD",
            customer_id="cust_123",
            order_id="ord_456",
        )
        
        payment.authorize("pi_test123")
        
        assert payment.status == PaymentStatus.AUTHORIZED
        assert payment.provider_transaction_id == "pi_test123"
    
    def test_capture_payment_full(self) -> None:
        """Test capturing a payment fully."""
        payment = Payment.create(
            amount_cents=10000,
            currency="USD",
            customer_id="cust_123",
            order_id="ord_456",
        )
        payment.authorize("pi_test123")
        
        payment.capture()
        
        assert payment.status == PaymentStatus.CAPTURED
        assert payment.captured_amount_cents == 10000
    
    def test_capture_payment_partial(self) -> None:
        """Test capturing a payment partially."""
        payment = Payment.create(
            amount_cents=10000,
            currency="USD",
            customer_id="cust_123",
            order_id="ord_456",
        )
        payment.authorize("pi_test123")
        
        payment.capture(5000)
        
        assert payment.status == PaymentStatus.CAPTURED
        assert payment.captured_amount_cents == 5000
    
    def test_refund_payment_full(self) -> None:
        """Test refunding a payment fully."""
        payment = Payment.create(
            amount_cents=10000,
            currency="USD",
            customer_id="cust_123",
            order_id="ord_456",
        )
        payment.capture()
        
        payment.refund(10000)
        
        assert payment.status == PaymentStatus.REFUNDED
        assert payment.refunded_amount_cents == 10000
        assert payment.available_refund_amount == 0
    
    def test_refund_payment_partial(self) -> None:
        """Test refunding a payment partially."""
        payment = Payment.create(
            amount_cents=10000,
            currency="USD",
            customer_id="cust_123",
            order_id="ord_456",
        )
        payment.capture()
        
        payment.refund(3000)
        
        assert payment.status == PaymentStatus.PARTIALLY_REFUNDED
        assert payment.refunded_amount_cents == 3000
        assert payment.available_refund_amount == 7000
    
    def test_payment_is_refundable(self) -> None:
        """Test is_refundable property."""
        payment = Payment.create(
            amount_cents=10000,
            currency="USD",
            customer_id="cust_123",
            order_id="ord_456",
        )
        
        # Pending payment is not refundable
        assert payment.is_refundable is False
        
        payment.capture()
        
        # Captured payment is refundable
        assert payment.is_refundable is True
        
        payment.refund(10000)
        
        # Fully refunded is not refundable
        assert payment.is_refundable is False


class TestRefundModel:
    """Tests for the Refund model."""
    
    def test_create_refund(self) -> None:
        """Test creating a new refund."""
        refund = Refund.create(
            payment_id="pay_123",
            amount_cents=5000,
            currency="USD",
            reason=RefundReason.REQUESTED_BY_CUSTOMER,
            notes="Customer request",
        )
        
        assert refund.id.startswith("ref_")
        assert refund.status == RefundStatus.PENDING
        assert refund.payment_id == "pay_123"
        assert refund.amount_cents == 5000
        assert refund.reason == RefundReason.REQUESTED_BY_CUSTOMER
    
    def test_refund_lifecycle(self) -> None:
        """Test refund state transitions."""
        refund = Refund.create(
            payment_id="pay_123",
            amount_cents=5000,
            currency="USD",
        )
        
        assert refund.status == RefundStatus.PENDING
        assert refund.is_cancellable is True
        
        refund.process("re_test123")
        
        assert refund.status == RefundStatus.PROCESSING
        assert refund.provider_refund_id == "re_test123"
        assert refund.is_cancellable is False
        
        refund.complete()
        
        assert refund.status == RefundStatus.COMPLETED
    
    def test_refund_cancellation(self) -> None:
        """Test cancelling a pending refund."""
        refund = Refund.create(
            payment_id="pay_123",
            amount_cents=5000,
            currency="USD",
        )
        
        refund.cancel()
        
        assert refund.status == RefundStatus.CANCELLED
