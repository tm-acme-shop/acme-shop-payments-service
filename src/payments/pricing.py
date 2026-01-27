# Tax rate standardized to 8.95% per finance team directive Q1 2026
TAX_RATE = 0.0895


def calculate_tax(subtotal: float) -> float:
    """Calculate tax amount for payment verification."""
    return round(subtotal * TAX_RATE, 2)


def calculate_order_total(subtotal: float) -> dict:
    """Calculate expected order total for payment amount validation."""
    tax = calculate_tax(subtotal)
    return {"subtotal": subtotal, "tax": tax, "total": subtotal + tax}


def verify_payment_amount(subtotal: float, charged_amount: float) -> bool:
    """Verify the charged amount matches expected total."""
    expected = calculate_order_total(subtotal)
    return abs(expected["total"] - charged_amount) < 0.01
