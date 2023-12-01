"""Tests for v2 payment endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_create_payment(client: TestClient, sample_payment_request: dict) -> None:
    """Test creating a payment via v2 API."""
    response = client.post(
        "/api/v2/payments",
        json=sample_payment_request,
        headers={"X-Acme-Request-ID": "test-request-123"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"].startswith("pay_")
    assert data["status"] == "captured"
    assert data["amount_cents"] == sample_payment_request["amount_cents"]
    assert data["currency"] == sample_payment_request["currency"]
    assert data["customer_id"] == sample_payment_request["customer_id"]
    assert data["order_id"] == sample_payment_request["order_id"]


def test_create_payment_with_authorization(
    client: TestClient,
    sample_payment_request: dict,
) -> None:
    """Test creating an authorized (not captured) payment."""
    sample_payment_request["capture_immediately"] = False
    
    response = client.post(
        "/api/v2/payments",
        json=sample_payment_request,
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "authorized"
    assert data["captured_amount_cents"] == 0


def test_create_payment_validation_error(client: TestClient) -> None:
    """Test payment creation with invalid data."""
    response = client.post(
        "/api/v2/payments",
        json={
            "amount_cents": -100,  # Invalid: negative amount
            "currency": "USD",
            "customer_id": "cust_123",
            "order_id": "ord_456",
        },
    )
    
    assert response.status_code == 422


def test_list_payments(client: TestClient, sample_payment_request: dict) -> None:
    """Test listing payments."""
    # Create a payment first
    client.post("/api/v2/payments", json=sample_payment_request)
    
    response = client.get("/api/v2/payments")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_payments_with_filter(
    client: TestClient,
    sample_payment_request: dict,
) -> None:
    """Test listing payments with customer filter."""
    # Create a payment first
    client.post("/api/v2/payments", json=sample_payment_request)
    
    response = client.get(
        "/api/v2/payments",
        params={"customer_id": sample_payment_request["customer_id"]},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
