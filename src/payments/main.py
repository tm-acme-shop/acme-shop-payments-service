"""
Main entry point for the AcmeShop Payments Service.

This service handles payment orchestration, processing payments through
multiple providers (Stripe, PayPal) and managing refunds and webhooks.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from payments.api.router import api_router
from payments.config import get_settings
from payments.feature_flags import load_feature_flags
from payments.logging_config import configure_logging, get_logger
from payments.version import __version__

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown."""
    # Startup
    configure_logging()
    load_feature_flags()
    
    # TODO(TEAM-PLATFORM): Add database connection pool initialization
    # TODO(TEAM-PAYMENTS): Initialize payment provider clients
    
    logger.info(
        "Payments service started",
        extra={
            "version": __version__,
            "environment": settings.environment,
            "port": settings.service_port,
        },
    )
    
    # Legacy startup logging - TODO(TEAM-PLATFORM): Remove after logging migration
    logging.info(f"Payments service v{__version__} starting on port {settings.service_port}")
    
    yield
    
    # Shutdown
    logger.info("Payments service shutting down", extra={"version": __version__})


app = FastAPI(
    title="AcmeShop Payments Service",
    description="Payment orchestration service for the AcmeShop platform",
    version=__version__,
    lifespan=lifespan,
)

# CORS middleware
# TODO(TEAM-SEC): Restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


def main() -> None:
    """Run the payments service."""
    # TODO(TEAM-PLATFORM): Use proper process manager in production
    uvicorn.run(
        "payments.main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
