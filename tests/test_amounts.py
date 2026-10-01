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


def test_format_amount_defaults_to_two_decimal_places() -> None:
    assert amounts.format_amount(CurrencyAmount(12.5, "USD")) == "12.50 USD"


@pytest.mark.parametrize(
    ("value", "precision", "expected"),
    [(12.6, 0, "13 EUR"), (1.25, 8, "1.25000000 EUR"), (0.001, 2, "0.00 EUR")],
)
def test_format_amount_uses_requested_display_precision(value: float, precision: int, expected: str) -> None:
    assert amounts.format_amount(CurrencyAmount(value, "EUR"), precision) == expected


@pytest.mark.parametrize("precision", [-1, 9, True, 2.0, "2", None])
def test_format_amount_rejects_invalid_precision(precision: object) -> None:
    with pytest.raises(InvalidAmount):
        amounts.format_amount(CurrencyAmount(1, "USD"), precision)


@pytest.mark.parametrize(
    "amount",
    [None, 1, {"value": 1, "currency": "USD"}, CurrencyAmount(float("nan"), "USD"), CurrencyAmount(0, "USD"), CurrencyAmount(1, "PLN")],
)
def test_format_amount_revalidates_input(amount: object) -> None:
    with pytest.raises(InvalidAmount):
        amounts.format_amount(amount)


def test_sum_amounts_accepts_a_generator_and_preserves_small_addends() -> None:
    values = (CurrencyAmount(value, "USD") for value in [1e16, 1, 1])
    assert amounts.sum_amounts(values) == CurrencyAmount(10000000000000002.0, "USD")


def test_sum_amounts_accepts_one_item() -> None:
    assert amounts.sum_amounts([CurrencyAmount(2.5, "UAH")]) == CurrencyAmount(2.5, "UAH")


@pytest.mark.parametrize(
    "values",
    [
        [],
        None,
        1,
        [None],
        [CurrencyAmount(1, "USD"), CurrencyAmount(1, "EUR")],
        [CurrencyAmount(1, "USD"), CurrencyAmount(float("nan"), "USD")],
        [CurrencyAmount(0, "USD")],
        [CurrencyAmount(True, "USD")],
        [CurrencyAmount(1, "PLN")],
        [CurrencyAmount(1e308, "USD"), CurrencyAmount(1e308, "USD")],
    ],
)
def test_sum_amounts_rejects_invalid_collections(values: object) -> None:
    with pytest.raises(InvalidAmount):
        amounts.sum_amounts(values)


def test_convert_amount_uses_explicit_target_units_per_source_unit() -> None:
    source = CurrencyAmount(12.5, "USD")
    assert amounts.convert_amount(source, "EUR", 0.8) == CurrencyAmount(10.0, "EUR")
    assert source == CurrencyAmount(12.5, "USD")


def test_convert_amount_accepts_unit_rate() -> None:
    assert amounts.convert_amount(CurrencyAmount(10, "GBP"), "UAH", 1) == CurrencyAmount(10, "UAH")


@pytest.mark.parametrize("rate", [0, -1, float("nan"), float("inf"), -float("inf"), True, "0.8", None])
def test_convert_amount_rejects_invalid_rate(rate: object) -> None:
    with pytest.raises(InvalidAmount):
        amounts.convert_amount(CurrencyAmount(10, "USD"), "EUR", rate)


@pytest.mark.parametrize("target", ["PLN", "eur", None, 1])
def test_convert_amount_rejects_invalid_target_currency(target: object) -> None:
    with pytest.raises(InvalidAmount):
        amounts.convert_amount(CurrencyAmount(10, "USD"), target, 0.8)


@pytest.mark.parametrize(
    "source",
    [None, 10, CurrencyAmount(0, "USD"), CurrencyAmount(float("inf"), "USD"), CurrencyAmount(10, "PLN")],
)
def test_convert_amount_revalidates_source(source: object) -> None:
    with pytest.raises(InvalidAmount):
        amounts.convert_amount(source, "EUR", 0.8)


@pytest.mark.parametrize(("value", "rate"), [(1e308, 2), (1e-300, 1e-300)])
def test_convert_amount_rejects_overflow_and_underflow(value: float, rate: float) -> None:
    with pytest.raises(InvalidAmount):
        amounts.convert_amount(CurrencyAmount(value, "USD"), "EUR", rate)
