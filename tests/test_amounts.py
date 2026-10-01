from dataclasses import FrozenInstanceError

import pytest

from legion_spike_validators.amounts import CurrencyAmount, InvalidAmount, validate


def test_valid_amount() -> None:
    assert validate(12.5, "USD") == CurrencyAmount(value=12.5, currency="USD")


def test_amount_is_immutable() -> None:
    amount = validate(100, "UAH")
    with pytest.raises(FrozenInstanceError):
        amount.value = 200


def test_invalid_amount_or_currency() -> None:
    with pytest.raises(InvalidAmount, match="amount must be > 0"):
        validate(0, "EUR")
    with pytest.raises(InvalidAmount, match="unsupported currency"):
        validate(1, "PLN")
