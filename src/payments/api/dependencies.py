"""
FastAPI dependencies for request handling.
"""

from typing import Annotated, Optional

from fastapi import Depends, Header, Request

from payments.interfaces.payment_client import PaymentClient
from payments.logging_config import create_request_logger, get_logger
from payments.providers.paypal_client import PayPalPaymentClient
from payments.providers.stripe_client import StripePaymentClient
from payments.services.payment_service import PaymentService
from payments.services.refund_service import RefundService
from payments.utils.headers import RequestContext, parse_request_context

logger = get_logger(__name__)


def get_request_context(request: Request) -> RequestContext:
    """
    Extract request context from headers.
    
    Extracts:
        - X-Acme-Request-ID: Correlation ID for distributed tracing
        - X-Legacy-User-Id: Legacy user identifier (deprecated)
        - X-User-Id: Current user identifier
    """
    return parse_request_context(request)


def get_request_id(
    x_acme_request_id: Annotated[Optional[str], Header()] = None,
) -> Optional[str]:
    """Get request ID from header."""
    return x_acme_request_id


def get_legacy_user_id(
    x_legacy_user_id: Annotated[Optional[str], Header()] = None,
) -> Optional[str]:
    """
    Get legacy user ID from header.
    
    TODO(TEAM-API): Remove after X-Legacy-User-Id header migration.
    """
    return x_legacy_user_id


def get_user_id(
    x_user_id: Annotated[Optional[str], Header()] = None,
    x_legacy_user_id: Annotated[Optional[str], Header()] = None,
) -> Optional[str]:
    """
    Get user ID from headers.
    
    Prefers X-User-Id but falls back to X-Legacy-User-Id for compatibility.
    """
    # TODO(TEAM-API): Remove X-Legacy-User-Id fallback after migration
    return x_user_id or x_legacy_user_id


def get_stripe_client() -> PaymentClient:
    """Get Stripe payment client instance."""
    return StripePaymentClient()


def get_paypal_client() -> PaymentClient:
    """Get PayPal payment client instance."""
    return PayPalPaymentClient()


def get_payment_client(
    provider: str = "stripe",
) -> PaymentClient:
    """
    Get payment client based on provider.
    
    TODO(TEAM-PAYMENTS): Inject via proper DI container.
    """
    clients: dict[str, PaymentClient] = {
        "stripe": StripePaymentClient(),
        "paypal": PayPalPaymentClient(),
    }
    return clients.get(provider, StripePaymentClient())


def get_payment_service(
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> PaymentService:
    """Get payment service instance."""
    return PaymentService(request_context=ctx)


def get_payment_service_v2(
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> PaymentService:
    """
    Get payment service for v2 API.
    
    Uses structured logging and modern payment flow.
    """
    service = PaymentService(request_context=ctx)
    service.set_api_version("v2")
    return service


def get_payment_service_legacy(
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> PaymentService:
    """
    Get payment service for legacy v1 API.
    
    TODO(TEAM-PAYMENTS): Remove after v1 deprecation.
    """
    service = PaymentService(request_context=ctx)
    service.set_api_version("v1")
    return service


def get_refund_service(
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> RefundService:
    """Get refund service instance."""
    return RefundService(request_context=ctx)


def get_refund_service_v2(
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> RefundService:
    """Get refund service for v2 API."""
    service = RefundService(request_context=ctx)
    service.set_api_version("v2")
    return service


RequestContextDep = Annotated[RequestContext, Depends(get_request_context)]
PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
PaymentServiceV2Dep = Annotated[PaymentService, Depends(get_payment_service_v2)]
PaymentServiceLegacyDep = Annotated[PaymentService, Depends(get_payment_service_legacy)]
RefundServiceDep = Annotated[RefundService, Depends(get_refund_service)]
RefundServiceV2Dep = Annotated[RefundService, Depends(get_refund_service_v2)]
