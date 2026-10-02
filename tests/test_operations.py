import pytest

from legion_spike_validators import amounts


def test_subtract_requires_same_currency_and_positive_remainder():
    usd = amounts.parse_amount
    assert amounts.subtract_amounts(usd("5 USD"), usd("2 USD")) == usd("3 USD")
    for left, right in [(usd("1 USD"), usd("1 EUR")),
                        (usd("1 USD"), usd("2 USD")),
                        (usd("1 USD"), usd("1 USD")), (None, usd("1 USD"))]:
        with pytest.raises(amounts.InvalidAmount):
            amounts.subtract_amounts(left, right)


def test_split_returns_equal_immutable_parts():
    source = amounts.parse_amount("12 USD")
    parts = amounts.split_amount(source, 3)
    assert isinstance(parts, tuple)
    assert parts == (amounts.parse_amount("4 USD"),) * 3
    assert amounts.sum_amounts(parts) == source
    assert amounts.split_amount(source, 1) == (source,)


@pytest.mark.parametrize("parts", [0, -1, True, 2.5, 1001])
def test_split_rejects_invalid_part_counts(parts):
    with pytest.raises(amounts.InvalidAmount):
        amounts.split_amount(amounts.parse_amount("1 EUR"), parts)
