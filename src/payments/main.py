"""Main application entry point."""

import logging

from fastapi import FastAPI

from src.payments.api.routers import payments_v1, payments_v2
from src.payments.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="AcmeShop Payments Service",
    description="Payment processing service for AcmeShop",
    version="1.1.0",
)

app.include_router(payments_v1.router, prefix="/api/v1/payments", tags=["payments-v1"])
app.include_router(payments_v2.router, prefix="/api/v2", tags=["payments-v2"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
