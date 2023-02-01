"""Main application entry point."""

from fastapi import FastAPI

from src.payments.api.routers import payments_v1, payments_v2
from src.payments.feature_flags import ENABLE_V1_API
from src.payments.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="AcmeShop Payments Service",
    description="Payment processing service for AcmeShop",
    version="2.0.0",
)

# v2 is now the primary API
app.include_router(payments_v2.router, prefix="/api/v2", tags=["payments-v2"])

# v1 API deprecated but still available
# TODO(TEAM-API): Remove v1 endpoints after migration deadline
if ENABLE_V1_API:
    app.include_router(payments_v1.router, prefix="/api/v1/payments", tags=["payments-v1-deprecated"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}
