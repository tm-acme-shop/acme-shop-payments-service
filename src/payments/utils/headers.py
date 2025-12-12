"""
HTTP header utilities for request context extraction.

Handles the extraction and management of request headers including:
- X-Acme-Request-ID: Distributed tracing correlation ID
- X-Legacy-User-Id: Deprecated user identifier header
- X-User-Id: Current user identifier header
"""

from dataclasses import dataclass
from typing import Optional

from fastapi import Request


@dataclass
class RequestContext:
    """
    Request context extracted from HTTP headers.
    
    Contains information about the current request that needs to be
    propagated through the service layer for logging and tracing.
    """
    
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    legacy_user_id: Optional[str] = None
    
    # TODO(TEAM-PLATFORM): Add tenant_id for multi-tenant support
    
    @property
    def effective_user_id(self) -> Optional[str]:
        """
        Get the effective user ID.
        
        Prefers the new X-User-Id header but falls back to X-Legacy-User-Id.
        """
        return self.user_id or self.legacy_user_id
    
    def to_dict(self) -> dict[str, Optional[str]]:
        """Convert to dictionary for logging."""
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "legacy_user_id": self.legacy_user_id,
        }


def parse_request_context(request: Request) -> RequestContext:
    """
    Parse request context from HTTP headers.
    
    Extracts common headers used for tracing and user identification.
    
    Headers:
        X-Acme-Request-ID: Correlation ID for distributed tracing
        X-User-Id: Current user identifier
        X-Legacy-User-Id: Deprecated user identifier (for backward compatibility)
    
    Args:
        request: FastAPI Request object
        
    Returns:
        RequestContext with extracted header values
    """
    return RequestContext(
        request_id=request.headers.get("X-Acme-Request-ID"),
        user_id=request.headers.get("X-User-Id"),
        legacy_user_id=request.headers.get("X-Legacy-User-Id"),
    )


def get_request_id(request: Request) -> Optional[str]:
    """
    Get the request ID from headers.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Request ID or None if not present
    """
    return request.headers.get("X-Acme-Request-ID")


def get_user_id(request: Request) -> Optional[str]:
    """
    Get the user ID from headers.
    
    Prefers X-User-Id but falls back to X-Legacy-User-Id.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        User ID or None if not present
    """
    return request.headers.get("X-User-Id") or request.headers.get("X-Legacy-User-Id")


def get_legacy_user_id(request: Request) -> Optional[str]:
    """
    Get the legacy user ID from headers.
    
    TODO(TEAM-API): Remove after X-Legacy-User-Id header migration.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Legacy user ID or None if not present
    """
    return request.headers.get("X-Legacy-User-Id")


def build_outbound_headers(context: RequestContext) -> dict[str, str]:
    """
    Build headers for outbound requests to other services.
    
    Propagates the request context to downstream services.
    
    Args:
        context: Current request context
        
    Returns:
        Dictionary of headers to include in outbound requests
    """
    headers: dict[str, str] = {}
    
    if context.request_id:
        headers["X-Acme-Request-ID"] = context.request_id
    
    if context.user_id:
        headers["X-User-Id"] = context.user_id
    
    # TODO(TEAM-API): Stop propagating X-Legacy-User-Id after migration
    if context.legacy_user_id:
        headers["X-Legacy-User-Id"] = context.legacy_user_id
    
    return headers


class LegacyHeaderParser:
    """
    Legacy header parser for v1 API compatibility.
    
    TODO(TEAM-API): Remove after v1 deprecation.
    """
    
    @staticmethod
    def parse_user_id(request: Request) -> Optional[str]:
        """
        Parse user ID using legacy header names.
        
        Supports older header names that may still be in use.
        """
        # Try new header first
        user_id = request.headers.get("X-User-Id")
        if user_id:
            return user_id
        
        # Fall back to legacy headers
        # TODO(TEAM-API): Remove these fallbacks after migration
        return (
            request.headers.get("X-Legacy-User-Id")
            or request.headers.get("X-UserId")  # Very old format
            or request.headers.get("UserId")  # Even older format
        )
    
    @staticmethod
    def parse_correlation_id(request: Request) -> Optional[str]:
        """
        Parse correlation ID using legacy header names.
        """
        return (
            request.headers.get("X-Acme-Request-ID")
            or request.headers.get("X-Request-ID")  # Alternative format
            or request.headers.get("X-Correlation-ID")  # Legacy format
        )
