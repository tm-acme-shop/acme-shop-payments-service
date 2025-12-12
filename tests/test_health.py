"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test basic health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "payments-service"
    assert "version" in data
    assert "timestamp" in data


def test_readiness_check(client: TestClient) -> None:
    """Test readiness check endpoint."""
    response = client.get("/health/ready")
    
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert "checks" in data


def test_liveness_check(client: TestClient) -> None:
    """Test liveness check endpoint."""
    response = client.get("/health/live")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_service_info(client: TestClient) -> None:
    """Test service info endpoint."""
    response = client.get("/health/info")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "payments-service"
    assert "v1" in data["api_versions"]
    assert "v2" in data["api_versions"]
    assert "stripe" in data["providers"]
    assert "paypal" in data["providers"]
