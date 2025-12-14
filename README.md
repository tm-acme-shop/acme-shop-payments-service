# AcmeShop Payments Service

Payment orchestration service for the AcmeShop platform. Handles payment processing, refunds, and webhook management with integrations to multiple payment providers (Stripe, PayPal).

## Overview

This service provides:
- **Payment Processing**: Create and manage payments via multiple providers
- **Refund Management**: Full and partial refunds
- **Webhook Handling**: Process provider callbacks for async events
- **Provider Abstraction**: Unified PaymentClient interface for all providers

## API Versions

⚠️ **Migration Notice**: API v1 endpoints are deprecated and will be removed in a future release.

| Version | Status | Description |
|---------|--------|-------------|
| `/api/v1/*` | **Deprecated** | Legacy endpoints, uses old logging and patterns |
| `/api/v2/*` | **Current** | Modern endpoints with structured logging |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m payments.main

# Or with uvicorn directly
uvicorn payments.main:app --reload --port 8002
```

## Configuration

Set environment variables or use `.env` file:

```bash
# Feature flags
ENABLE_LEGACY_PAYMENTS=true    # Enable deprecated v1 endpoints
ENABLE_V1_API=true             # Global v1 API toggle

# Provider configuration
STRIPE_API_KEY=sk_test_...
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...

# Service configuration
PAYMENTS_SERVICE_PORT=8002
LOG_LEVEL=INFO
```

## Project Structure

```
src/payments/
├── api/                    # FastAPI routers and schemas
│   ├── routers/           # Endpoint handlers (v1 and v2)
│   └── schemas/           # Pydantic request/response models
├── interfaces/            # Abstract base classes
├── providers/             # Payment provider implementations
├── services/              # Business logic
├── models/                # Domain models
├── utils/                 # Utilities (crypto, headers)
└── infra/                 # Infrastructure (database)
```

## Development

```bash
# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/
```

## API Endpoints

### Health
- `GET /health` - Service health check

### Payments (v2 - Current)
- `POST /api/v2/payments` - Create a payment
- `GET /api/v2/payments/{id}` - Get payment details
- `POST /api/v2/payments/{id}/capture` - Capture authorized payment

### Payments (v1 - Deprecated)
- `POST /api/v1/payments` - Create a payment (deprecated)
- `GET /api/v1/payments/{id}` - Get payment details (deprecated)

### Refunds (v2 - Current)
- `POST /api/v2/refunds` - Create a refund
- `GET /api/v2/refunds/{id}` - Get refund details

### Webhooks
- `POST /webhooks/stripe` - Stripe webhook handler
- `POST /webhooks/paypal` - PayPal webhook handler

## License

MIT License
