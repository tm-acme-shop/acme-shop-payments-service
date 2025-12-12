"""Tests for v2 refund endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_create_refund(client: TestClient, sample_refund_request: dict) -> None:
    """Test creating a refund via v2 API."""
    response = client.post(
        "/api/v2/refunds",
        json=sample_refund_request,
        headers={"X-Acme-Request-ID": "test-request-123"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"].startswith("ref_")
    assert data["status"] == "completed"
    assert data["amount_cents"] == sample_refund_request["amount_cents"]
    assert data["payment_id"] == sample_refund_request["payment_id"]


def test_create_full_refund(client: TestClient) -> None:
    """Test creating a full refund (no amount specified)."""
    response = client.post(
        "/api/v2/refunds",
        json={
            "payment_id": "pay_demo123",
            "reason": "order_cancelled",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["reason"] == "order_cancelled"


def test_list_refunds(client: TestClient, sample_refund_request: dict) -> None:
    """Test listing refunds."""
    # Create a refund first
    client.post("/api/v2/refunds", json=sample_refund_request)
    
    response = client.get("/api/v2/refunds")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_refunds_by_payment(
    client: TestClient,
    sample_refund_request: dict,
) -> None:
    """Test listing refunds filtered by payment."""
    # Create a refund first
    client.post("/api/v2/refunds", json=sample_refund_request)
    
    response = client.get(
        "/api/v2/refunds",
        params={"payment_id": sample_refund_request["payment_id"]},
    )
    
    assert response.status_code == 200
