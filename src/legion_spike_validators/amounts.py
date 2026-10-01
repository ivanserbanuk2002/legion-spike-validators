import math
from dataclasses import dataclass


class InvalidAmount(ValueError):
    pass


@dataclass(frozen=True)
class CurrencyAmount:
    value: float
    currency: str


def validate(amount: float, currency: str) -> CurrencyAmount:
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise InvalidAmount("amount must be a finite number")
    try:
        finite = math.isfinite(amount)
    except OverflowError as exc:
        raise InvalidAmount("amount must be a finite number") from exc
    if not finite:
        raise InvalidAmount("amount must be a finite number")
    if amount <= 0:
        raise InvalidAmount(f"amount must be > 0, got {amount}")
    if not isinstance(currency, str) or currency not in ("USD", "EUR", "GBP", "UAH"):
        raise InvalidAmount(f"unsupported currency: {currency}")
    return CurrencyAmount(value=amount, currency=currency)


def parse_amount(text: str) -> CurrencyAmount:
    """Parse a whitespace-separated number and currency, e.g. ``12.50 usd``."""
    if not isinstance(text, str):
        raise InvalidAmount("amount text must be a string")
    parts = text.split()
    if len(parts) != 2:
        raise InvalidAmount("expected amount and currency, e.g. '12.50 USD'")
    try:
        value = float(parts[0])
    except ValueError as exc:
        raise InvalidAmount("invalid amount number") from exc
    return validate(value, parts[1].upper())
