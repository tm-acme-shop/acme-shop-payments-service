"""Feature flags for the payments service."""

import os

ENABLE_LEGACY_PAYMENTS: bool = os.getenv("ENABLE_LEGACY_PAYMENTS", "true").lower() == "true"
ENABLE_V1_API: bool = os.getenv("ENABLE_V1_API", "true").lower() == "true"
