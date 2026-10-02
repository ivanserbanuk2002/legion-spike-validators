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
