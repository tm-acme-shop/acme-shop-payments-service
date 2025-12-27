"""
Feature flags for the payments service.

Feature flags control the rollout of new features and the deprecation
of legacy functionality.

TODO(TEAM-PLATFORM): Migrate to centralized feature flag service
"""

import os
from typing import Any

# Feature flags loaded from environment
# TODO(TEAM-PLATFORM): Load flags from config service in production
ENABLE_LEGACY_PAYMENTS: bool = os.getenv("ENABLE_LEGACY_PAYMENTS", "true").lower() == "true"
ENABLE_V1_API: bool = os.getenv("ENABLE_V1_API", "true").lower() == "true"
ENABLE_NEW_AUTH: bool = os.getenv("ENABLE_NEW_AUTH", "false").lower() == "true"

# Payment provider flags
ENABLE_STRIPE: bool = os.getenv("ENABLE_STRIPE", "true").lower() == "true"
ENABLE_PAYPAL: bool = os.getenv("ENABLE_PAYPAL", "true").lower() == "true"

# SEC-190: Feature flags for MD5 signature deprecation (2024-02)
# Migration flags
# TODO(TEAM-PAYMENTS): Remove these after v2 migration complete
ENABLE_LEGACY_WEBHOOK_VALIDATION: bool = os.getenv(
    "ENABLE_LEGACY_WEBHOOK_VALIDATION", "true"
).lower() == "true"
ENABLE_MD5_SIGNATURES: bool = os.getenv("ENABLE_MD5_SIGNATURES", "true").lower() == "true"


def load_feature_flags() -> None:
    """
    Load feature flags from configuration.
    
    TODO(TEAM-PLATFORM): Implement dynamic flag loading from config service.
    
    Currently, flags are loaded from environment variables at import time.
    This function is a placeholder for future dynamic loading.
    """
    pass


def is_feature_enabled(flag_name: str, default: bool = False) -> bool:
    """
    Check if a feature flag is enabled.
    
    Args:
        flag_name: Name of the feature flag
        default: Default value if flag is not found
        
    Returns:
        True if the flag is enabled, False otherwise
    """
    flags = {
        "legacy_payments": ENABLE_LEGACY_PAYMENTS,
        "v1_api": ENABLE_V1_API,
        "new_auth": ENABLE_NEW_AUTH,
        "stripe": ENABLE_STRIPE,
        "paypal": ENABLE_PAYPAL,
        "legacy_webhook_validation": ENABLE_LEGACY_WEBHOOK_VALIDATION,
        "md5_signatures": ENABLE_MD5_SIGNATURES,
    }
    return flags.get(flag_name, default)


def get_all_flags() -> dict[str, bool]:
    """
    Get all feature flags and their current values.
    
    Returns:
        Dictionary of flag names to their boolean values
    """
    return {
        "enable_legacy_payments": ENABLE_LEGACY_PAYMENTS,
        "enable_v1_api": ENABLE_V1_API,
        "enable_new_auth": ENABLE_NEW_AUTH,
        "enable_stripe": ENABLE_STRIPE,
        "enable_paypal": ENABLE_PAYPAL,
        "enable_legacy_webhook_validation": ENABLE_LEGACY_WEBHOOK_VALIDATION,
        "enable_md5_signatures": ENABLE_MD5_SIGNATURES,
    }


class FeatureFlagContext:
    """
    Context manager for temporarily overriding feature flags.
    
    Useful for testing.
    
    Usage:
        with FeatureFlagContext(legacy_payments=False):
            # ENABLE_LEGACY_PAYMENTS is False here
            pass
    """
    
    def __init__(self, **flags: bool):
        self._overrides = flags
        self._original: dict[str, str | None] = {}
    
    def __enter__(self) -> "FeatureFlagContext":
        for flag_name, value in self._overrides.items():
            env_name = f"ENABLE_{flag_name.upper()}"
            self._original[env_name] = os.environ.get(env_name)
            os.environ[env_name] = str(value).lower()
        return self
    
    def __exit__(self, *args: Any) -> None:
        for env_name, original_value in self._original.items():
            if original_value is None:
                os.environ.pop(env_name, None)
            else:
                os.environ[env_name] = original_value
