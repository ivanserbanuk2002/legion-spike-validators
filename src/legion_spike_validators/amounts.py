from dataclasses import dataclass


class InvalidAmount(ValueError):
    pass


@dataclass(frozen=True)
class CurrencyAmount:
    value: float
    currency: str


def validate(amount: float, currency: str) -> CurrencyAmount:
    if amount <= 0:
        raise InvalidAmount(f"amount must be > 0, got {amount}")
    if currency not in ("USD", "EUR", "GBP", "UAH"):
        raise InvalidAmount(f"unsupported currency: {currency}")
    return CurrencyAmount(value=amount, currency=currency)
