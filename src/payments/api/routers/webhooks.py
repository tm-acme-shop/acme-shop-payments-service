"""
Webhook handlers for payment providers.

Handles incoming webhooks from Stripe and PayPal to update payment
and refund statuses.
"""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Header, HTTPException, Request

from payments.api.schemas.webhooks import (
    PayPalWebhookPayload,
    StripeWebhookPayload,
    WebhookResponse,
)
from payments.config import get_settings
from payments.errors import WebhookSignatureError
from payments.feature_flags import ENABLE_LEGACY_WEBHOOK_VALIDATION
from payments.logging_config import get_logger
from payments.utils.crypto_legacy import compute_sha1, verify_hmac_sha256

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.post(
    "/stripe",
    response_model=WebhookResponse,
    summary="Stripe webhook handler",
)
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: Annotated[Optional[str], Header(alias="Stripe-Signature")] = None,
) -> WebhookResponse:
    """
    Handle incoming Stripe webhooks.
    
    Verifies the webhook signature and processes the event.
    """
    body = await request.body()
    
    # Verify webhook signature
    if settings.stripe_webhook_secret and stripe_signature:
        try:
            _verify_stripe_signature(body, stripe_signature, settings.stripe_webhook_secret)
        except WebhookSignatureError as e:
            logger.error(
                "Stripe webhook signature verification failed",
                extra={"error": str(e)},
            )
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse the payload
    import json
    payload_data = json.loads(body)
    payload = StripeWebhookPayload(**payload_data)
    
    logger.info(
        "Received Stripe webhook",
        extra={
            "event_id": payload.id,
            "event_type": payload.type,
            "livemode": payload.livemode,
        },
    )
    
    # Process based on event type
    processed = await _process_stripe_event(payload)
    
    return WebhookResponse(
        received=True,
        event_id=payload.id,
        event_type=payload.type,
        processed=processed,
        message="Webhook processed successfully" if processed else "Event type not handled",
    )


@router.post(
    "/paypal",
    response_model=WebhookResponse,
    summary="PayPal webhook handler",
)
async def handle_paypal_webhook(
    request: Request,
    paypal_transmission_id: Annotated[
        Optional[str], Header(alias="PayPal-Transmission-Id")
    ] = None,
    paypal_transmission_sig: Annotated[
        Optional[str], Header(alias="PayPal-Transmission-Sig")
    ] = None,
) -> WebhookResponse:
    """
    Handle incoming PayPal webhooks.
    """
    body = await request.body()
    
    # TODO(TEAM-SEC): Implement proper PayPal signature verification
    if ENABLE_LEGACY_WEBHOOK_VALIDATION and paypal_transmission_sig:
        # Legacy validation using SHA1 - TODO(TEAM-SEC): Replace with proper PayPal SDK
        legacy_hash = compute_sha1(body)
        logging.info("PayPal webhook legacy hash: %s", legacy_hash)
    
    import json
    payload_data = json.loads(body)
    payload = PayPalWebhookPayload(**payload_data)
    
    logger.info(
        "Received PayPal webhook",
        extra={
            "event_id": payload.id,
            "event_type": payload.event_type,
            "resource_type": payload.resource_type,
        },
    )
    
    processed = await _process_paypal_event(payload)
    
    return WebhookResponse(
        received=True,
        event_id=payload.id,
        event_type=payload.event_type,
        processed=processed,
    )


def _verify_stripe_signature(
    payload: bytes,
    signature: str,
    secret: str,
) -> None:
    """
    Verify Stripe webhook signature.
    
    TODO(TEAM-SEC): Use official Stripe SDK for verification.
    """
    # Parse signature header
    elements = dict(item.split("=") for item in signature.split(",") if "=" in item)
    timestamp = elements.get("t")
    v1_signature = elements.get("v1")
    
    if not timestamp or not v1_signature:
        raise WebhookSignatureError("stripe", "Missing signature elements")
    
    # Verify signature
    signed_payload = f"{timestamp}.".encode() + payload
    if not verify_hmac_sha256(signed_payload, secret, v1_signature):
        raise WebhookSignatureError("stripe", "Signature mismatch")


async def _process_stripe_event(payload: StripeWebhookPayload) -> bool:
    """
    Process a Stripe webhook event.
    
    Returns True if the event was handled, False otherwise.
    """
    event_handlers = {
        "payment_intent.succeeded": _handle_stripe_payment_succeeded,
        "payment_intent.payment_failed": _handle_stripe_payment_failed,
        "charge.refunded": _handle_stripe_refund,
    }
    
    handler = event_handlers.get(payload.type)
    if handler:
        await handler(payload)
        return True
    
    logger.info(
        "Unhandled Stripe event type",
        extra={"event_type": payload.type},
    )
    return False


async def _process_paypal_event(payload: PayPalWebhookPayload) -> bool:
    """
    Process a PayPal webhook event.
    """
    event_handlers = {
        "PAYMENT.CAPTURE.COMPLETED": _handle_paypal_capture_completed,
        "PAYMENT.CAPTURE.DENIED": _handle_paypal_capture_denied,
        "PAYMENT.CAPTURE.REFUNDED": _handle_paypal_refund,
    }
    
    handler = event_handlers.get(payload.event_type)
    if handler:
        await handler(payload)
        return True
    
    logger.info(
        "Unhandled PayPal event type",
        extra={"event_type": payload.event_type},
    )
    return False


async def _handle_stripe_payment_succeeded(payload: StripeWebhookPayload) -> None:
    """Handle Stripe payment_intent.succeeded event."""
    data = payload.data.get("object", {})
    payment_intent_id = data.get("id")
    
    logger.info(
        "Stripe payment succeeded",
        extra={
            "payment_intent_id": payment_intent_id,
            "amount": data.get("amount"),
            "currency": data.get("currency"),
        },
    )
    
    # TODO(TEAM-PAYMENTS): Update payment status in database


async def _handle_stripe_payment_failed(payload: StripeWebhookPayload) -> None:
    """Handle Stripe payment_intent.payment_failed event."""
    data = payload.data.get("object", {})
    payment_intent_id = data.get("id")
    
    logger.error(
        "Stripe payment failed",
        extra={
            "payment_intent_id": payment_intent_id,
            "error": data.get("last_payment_error"),
        },
    )


async def _handle_stripe_refund(payload: StripeWebhookPayload) -> None:
    """Handle Stripe charge.refunded event."""
    data = payload.data.get("object", {})
    
    logger.info(
        "Stripe refund processed",
        extra={
            "charge_id": data.get("id"),
            "amount_refunded": data.get("amount_refunded"),
        },
    )


async def _handle_paypal_capture_completed(payload: PayPalWebhookPayload) -> None:
    """Handle PayPal PAYMENT.CAPTURE.COMPLETED event."""
    resource = payload.resource
    
    logger.info(
        "PayPal capture completed",
        extra={
            "capture_id": resource.get("id"),
            "amount": resource.get("amount"),
        },
    )


async def _handle_paypal_capture_denied(payload: PayPalWebhookPayload) -> None:
    """Handle PayPal PAYMENT.CAPTURE.DENIED event."""
    resource = payload.resource
    
    logger.error(
        "PayPal capture denied",
        extra={
            "capture_id": resource.get("id"),
            "status": resource.get("status"),
        },
    )


async def _handle_paypal_refund(payload: PayPalWebhookPayload) -> None:
    """Handle PayPal PAYMENT.CAPTURE.REFUNDED event."""
    resource = payload.resource
    
    logger.info(
        "PayPal refund processed",
        extra={"refund_id": resource.get("id")},
    )
