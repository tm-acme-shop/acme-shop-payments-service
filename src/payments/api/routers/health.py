"""Health check endpoints."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter

from payments.feature_flags import get_all_flags
from payments.logging_config import get_logger
from payments.version import __version__

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def health_check() -> dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns service status, version, and timestamp.
    """
    logger.info("Health check requested", extra={"endpoint": "/health"})
    
    return {
        "status": "healthy",
        "service": "payments-service",
        "version": __version__,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready")
async def readiness_check() -> dict[str, Any]:
    """
    Readiness check for Kubernetes.
    
    Verifies service is ready to accept traffic.
    """
    # TODO(TEAM-PLATFORM): Add database connection check
    # TODO(TEAM-PLATFORM): Add payment provider connectivity check
    
    return {
        "ready": True,
        "checks": {
            "database": "ok",
            "stripe": "ok",
            "paypal": "ok",
        },
    }


@router.get("/live")
async def liveness_check() -> dict[str, str]:
    """
    Liveness check for Kubernetes.
    
    Simple check that the service is running.
    """
    return {"status": "alive"}


@router.get("/info")
async def service_info() -> dict[str, Any]:
    """
    Detailed service information.
    
    Returns version, feature flags, and configuration info.
    """
    return {
        "service": "payments-service",
        "version": __version__,
        "api_versions": ["v1", "v2"],
        "feature_flags": get_all_flags(),
        "providers": ["stripe", "paypal"],
    }
