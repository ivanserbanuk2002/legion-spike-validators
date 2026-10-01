from dataclasses import FrozenInstanceError

import pytest

from legion_spike_validators import amounts
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


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), True, "12.50", None, 10**1000])
def test_validate_rejects_nonfinite_or_nonnumeric_values(value: object) -> None:
    with pytest.raises(InvalidAmount):
        validate(value, "USD")


@pytest.mark.parametrize("currency", [None, 1, ["USD"], "usd"])
def test_validate_rejects_invalid_currency(currency: object) -> None:
    with pytest.raises(InvalidAmount):
        validate(1, currency)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("12.50 usd", CurrencyAmount(12.5, "USD")), ("  2\tEur\n", CurrencyAmount(2.0, "EUR")), ("1e2 GBP", CurrencyAmount(100.0, "GBP"))],
)
def test_parse_amount_normalises_currency(text: str, expected: CurrencyAmount) -> None:
    assert amounts.parse_amount(text) == expected


@pytest.mark.parametrize("text", ["", "12.50", "12 USD extra", "USD 12", "0 USD", "-2 USD", "nan USD", "inf USD", "1e309 USD", "12 PLN", None, 12])
def test_parse_amount_rejects_invalid_input(text: object) -> None:
    with pytest.raises(InvalidAmount):
        amounts.parse_amount(text)
