"""
Tests for v1 payment endpoints (deprecated).

TODO(TEAM-API): Remove after v1 deprecation deadline.
"""

import pytest
from fastapi.testclient import TestClient


def test_create_payment_legacy(
    client: TestClient,
    sample_payment_request_v1: dict,
) -> None:
    """Test creating a payment via deprecated v1 API."""
    response = client.post(
        "/api/v1/payments",
        json=sample_payment_request_v1,
        headers={
            "X-Acme-Request-ID": "test-request-123",
            "X-Legacy-User-Id": "legacy-user-456",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["payment_id"].startswith("PAY-")
    assert data["status_code"] == "COMPLETED"
    assert data["amount"] == sample_payment_request_v1["amount"]
    assert data["currency_code"] == sample_payment_request_v1["currency_code"]
    assert data["user_id"] == sample_payment_request_v1["user_id"]


def test_create_payment_legacy_with_idempotency(
    client: TestClient,
    sample_payment_request_v1: dict,
) -> None:
    """Test creating a payment with idempotency key."""
    response = client.post(
        "/api/v1/payments",
        json=sample_payment_request_v1,
        headers={"X-Idempotency-Key": "test-idempotency-key"},
    )
    
    assert response.status_code == 200


def test_get_payment_legacy(client: TestClient) -> None:
    """Test getting a payment via v1 API."""
    # First create a payment
    create_response = client.post(
        "/api/v1/payments",
        json={
            "amount": 5000,
            "currency_code": "USD",
            "user_id": "user_test",
            "order_reference": "ORD-TEST",
        },
    )
    
    payment_id = create_response.json()["payment_id"]
    
    # Then fetch it
    response = client.get(f"/api/v1/payments/{payment_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["payment_id"] == payment_id


def test_get_payment_legacy_not_found(client: TestClient) -> None:
    """Test getting a non-existent payment."""
    response = client.get("/api/v1/payments/PAY-NONEXISTENT123456")
    
    assert response.status_code == 404
