# AcmeShop Payments Service

Payment processing service for AcmeShop platform.

## Overview

This service handles payment processing for the AcmeShop e-commerce platform.

## API Endpoints

### Payments API (v1)

- `POST /api/v1/payments` - Create a new payment
- `GET /api/v1/payments/{payment_id}` - Get payment details
- `POST /api/v1/payments/{payment_id}/refund` - Refund a payment

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
pip install -r requirements.txt
```

### Running

```bash
uvicorn src.payments.main:app --reload
```

### Testing

```bash
pytest tests/ -v
```

## Environment Variables

See `.env.example` for configuration options.
