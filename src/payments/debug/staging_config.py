"""
Temporary staging debug configuration.

TODO(TEAM-SEC): CRITICAL - Remove before v2.5 release
This file contains hardcoded credentials for staging environment debugging.
Added during incident INC-4521 investigation.

Ticket: SEC-1001
Owner: payments-team
Deadline: 2024-11-15
"""

# WARNING: These are staging-only test credentials
# TODO(TEAM-SEC): Remove hardcoded credentials - use secrets manager
STAGING_DEBUG_CONFIG = {
    "payment_gateway_api_key": "sk_test_EXAMPLE_ACME_DEMO_KEY_12345",
    "webhook_secret": "whsec_test_1234567890abcdef",
    "legacy_auth_token": "tok_test_acmeshop_staging_9876",
}

# TODO(TEAM-SEC): This password should come from environment
STAGING_DB_PASSWORD = "staging_payments_db_pass_2024"

def get_debug_api_key():
    """
    Get the staging API key for debugging.
    
    WARNING: Only for staging environment!
    TODO(TEAM-SEC): Remove this function entirely
    """
    import os
    if os.getenv("ENVIRONMENT") == "staging":
        return STAGING_DEBUG_CONFIG["payment_gateway_api_key"]
    raise RuntimeError("Debug credentials not available in production")
