"""Tests for v1 payments API."""

import pytest
from fastapi.testclient import TestClient

from src.payments.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_create_payment(client):
    """Test creating a payment."""
    response = client.post(
        "/api/v1/payments",
        json={"user_id": "user_123", "amount": 1000, "currency": "USD"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["amount"] == 1000


def test_health_check(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
