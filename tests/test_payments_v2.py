"""Tests for v2 payments API."""

import pytest
from fastapi.testclient import TestClient

from src.payments.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_create_payment_v2(client):
    """Test creating a payment via v2 API."""
    response = client.post(
        "/api/v2/payments",
        json={"user_id": "user_123", "amount": 1000, "currency": "USD"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "completed"
