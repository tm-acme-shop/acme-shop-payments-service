"""Configuration management for the payments service."""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    service_name: str = "payments-service"
    service_port: int = 8002
    service_host: str = "0.0.0.0"
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = False

    # Feature Flags
    # TODO(TEAM-PAYMENTS): Remove ENABLE_LEGACY_PAYMENTS after v2 migration complete
    enable_legacy_payments: bool = True
    enable_v1_api: bool = True
    enable_legacy_auth: bool = False

    # Stripe Configuration
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

    # PayPal Configuration
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    paypal_environment: str = "sandbox"

    # Database Configuration
    database_url: str = "postgresql://payments:password@localhost:5432/payments_db"

    # Service URLs
    users_service_url: str = "http://localhost:8001"
    orders_service_url: str = "http://localhost:8003"
    notifications_service_url: str = "http://localhost:8004"

    # Legacy Settings
    # TODO(TEAM-PAYMENTS): Remove these after full v2 migration
    legacy_payment_provider: str = "stripe"
    legacy_webhook_validation: bool = True

    class Config:
        env_prefix = ""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_legacy_config() -> dict:
    """
    Get legacy configuration for backward compatibility.
    
    TODO(TEAM-PAYMENTS): Remove this function after v2 migration.
    """
    # TODO(TEAM-SEC): This exposes configuration insecurely, migrate to secure config
    settings = get_settings()
    return {
        "provider": settings.legacy_payment_provider,
        "validate_webhooks": settings.legacy_webhook_validation,
        "api_version": "v1",
    }
