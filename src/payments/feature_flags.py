"""
Feature flags for the payments service.

TODO(TEAM-PLATFORM): Migrate to centralized feature flag service.
"""

import os

# Legacy payment flags
# TODO(TEAM-PAYMENTS): Remove after v2 migration complete
ENABLE_LEGACY_PAYMENTS: bool = os.getenv("ENABLE_LEGACY_PAYMENTS", "true").lower() == "true"
ENABLE_V1_API: bool = os.getenv("ENABLE_V1_API", "true").lower() == "true"
ENABLE_LEGACY_AUTH: bool = os.getenv("ENABLE_LEGACY_AUTH", "false").lower() == "true"

# Payment provider flags
ENABLE_STRIPE: bool = os.getenv("ENABLE_STRIPE", "true").lower() == "true"
ENABLE_PAYPAL: bool = os.getenv("ENABLE_PAYPAL", "true").lower() == "true"


def is_feature_enabled(flag_name: str, default: bool = False) -> bool:
    """Check if a feature flag is enabled."""
    flags = {
        "legacy_payments": ENABLE_LEGACY_PAYMENTS,
        "v1_api": ENABLE_V1_API,
        "legacy_auth": ENABLE_LEGACY_AUTH,
        "stripe": ENABLE_STRIPE,
        "paypal": ENABLE_PAYPAL,
    }
    return flags.get(flag_name, default)
