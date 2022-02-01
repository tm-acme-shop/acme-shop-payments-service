"""Main application entry point."""

import logging

from fastapi import FastAPI

from src.payments.api.routers import payments_v1

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AcmeShop Payments Service",
    description="Payment processing service for AcmeShop",
    version="1.0.0",
)

app.include_router(payments_v1.router, prefix="/api/v1/payments", tags=["payments"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
