import math
from collections.abc import Iterable
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


def format_amount(amount: CurrencyAmount, decimal_places: int = 2) -> str:
    """Format a validated amount for display using 0 to 8 decimal places."""
    if not isinstance(amount, CurrencyAmount):
        raise InvalidAmount("expected a CurrencyAmount")
    validate(amount.value, amount.currency)
    if type(decimal_places) is not int or not 0 <= decimal_places <= 8:
        raise InvalidAmount("decimal_places must be an integer from 0 to 8")
    return f"{amount.value:.{decimal_places}f} {amount.currency}"


def sum_amounts(amounts: Iterable[CurrencyAmount]) -> CurrencyAmount:
    """Sum a nonempty collection of positive amounts in one currency."""
    try:
        iterator = iter(amounts)
    except TypeError as exc:
        raise InvalidAmount("expected an iterable of CurrencyAmount values") from exc
    values = []
    currency = None
    for amount in iterator:
        if not isinstance(amount, CurrencyAmount):
            raise InvalidAmount("expected a CurrencyAmount")
        validate(amount.value, amount.currency)
        if currency is not None and amount.currency != currency:
            raise InvalidAmount("cannot sum different currencies")
        currency = amount.currency
        values.append(amount.value)
    if not values:
        raise InvalidAmount("cannot sum an empty collection")
    try:
        total = math.fsum(values)
    except OverflowError as exc:
        raise InvalidAmount("amount sum exceeds the finite numeric range") from exc
    return validate(total, currency)


def convert_amount(amount: CurrencyAmount, target_currency: str, rate: float) -> CurrencyAmount:
    """Multiply by a caller-provided rate in target units per source unit."""
    if not isinstance(amount, CurrencyAmount):
        raise InvalidAmount("expected a CurrencyAmount")
    validate(amount.value, amount.currency)
    validate(rate, target_currency)
    return validate(amount.value * rate, target_currency)


def subtract_amounts(left: CurrencyAmount, right: CurrencyAmount) -> CurrencyAmount:
    """Subtract same-currency amounts; the remainder must stay positive."""
    if not isinstance(left, CurrencyAmount) or not isinstance(right, CurrencyAmount):
        raise InvalidAmount("expected CurrencyAmount values")
    validate(left.value, left.currency)
    validate(right.value, right.currency)
    if left.currency != right.currency:
        raise InvalidAmount("cannot subtract different currencies")
    return validate(left.value - right.value, left.currency)


def split_amount(amount: CurrencyAmount, parts: int) -> tuple[CurrencyAmount, ...]:
    """Split into 1 to 1000 equal float-valued parts without monetary rounding."""
    if not isinstance(amount, CurrencyAmount):
        raise InvalidAmount("expected a CurrencyAmount")
    validate(amount.value, amount.currency)
    if type(parts) is not int or not 1 <= parts <= 1000:
        raise InvalidAmount("parts must be an integer from 1 to 1000")
    part = validate(amount.value / parts, amount.currency)
    return (part,) * parts


def compare_amounts(left: CurrencyAmount, right: CurrencyAmount) -> int:
    """Return -1, 0 or 1 for validated values in the same currency."""
    if not isinstance(left, CurrencyAmount) or not isinstance(right, CurrencyAmount):
        raise InvalidAmount("expected CurrencyAmount values")
    validate(left.value, left.currency)
    validate(right.value, right.currency)
    if left.currency != right.currency:
        raise InvalidAmount("cannot compare different currencies")
    return (left.value > right.value) - (left.value < right.value)
