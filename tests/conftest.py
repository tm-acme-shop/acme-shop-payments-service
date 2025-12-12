"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from payments.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_payment_request() -> dict:
    """Sample payment request for testing."""
    return {
        "amount_cents": 9999,
        "currency": "USD",
        "customer_id": "cust_test123",
        "order_id": "ord_test456",
        "provider": "stripe",
        "description": "Test payment",
        "capture_immediately": True,
    }


@pytest.fixture
def sample_payment_request_v1() -> dict:
    """Sample v1 payment request for testing."""
    return {
        "amount": 9999,
        "currency_code": "USD",
        "user_id": "user_test123",
        "order_reference": "ORD-TEST456",
        "payment_method": "card",
    }


@pytest.fixture
def sample_refund_request() -> dict:
    """Sample refund request for testing."""
    return {
        "payment_id": "pay_demo123",
        "amount_cents": 5000,
        "reason": "requested_by_customer",
        "notes": "Test refund",
    }


@pytest.fixture
def sample_refund_request_v1() -> dict:
    """Sample v1 refund request for testing."""
    return {
        "payment_reference": "PAY-DEMO123",
        "refund_amount": 5000,
        "reason_code": "CUSTOMER_REQUEST",
    }
