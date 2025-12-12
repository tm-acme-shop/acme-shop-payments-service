"""
Main API router aggregating all sub-routers.
"""

from fastapi import APIRouter

from payments.api.routers import (
    health,
    payments_v1,
    payments_v2,
    refunds_v1,
    refunds_v2,
    webhooks,
)
from payments.feature_flags import ENABLE_V1_API

api_router = APIRouter()

# Health check - always included
api_router.include_router(health.router, prefix="/health", tags=["health"])

# V2 API - current version
api_router.include_router(payments_v2.router, prefix="/api/v2", tags=["payments-v2"])
api_router.include_router(refunds_v2.router, prefix="/api/v2", tags=["refunds-v2"])

# V1 API - deprecated
# TODO(TEAM-API): Remove v1 endpoints after migration deadline
if ENABLE_V1_API:
    api_router.include_router(payments_v1.router, prefix="/api/v1", tags=["payments-v1"])
    api_router.include_router(refunds_v1.router, prefix="/api/v1", tags=["refunds-v1"])

# Webhooks - provider-specific endpoints
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
