"""Configuration for the payments service."""

import os


class Config:
    """Application configuration."""
    
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8002"))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "")


config = Config()
