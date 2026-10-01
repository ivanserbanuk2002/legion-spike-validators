# legion-spike-validators

Shared amount-validation helpers for `legion-spike-trade-router`.
Internal package-distribution spike; installation requires repository access.
**Status:** spike — planned replacement: `@legion/shared` after the monolith split (ETA Q3, unconfirmed).
```bash
pip install "git+https://github.com/ivanserbanuk2002/legion-spike-validators.git#egg=legion-spike-validators"
```

Helpers live in `legion_spike_validators.amounts`. `validate(12.5, "USD")`
accepts finite positive Python `int`/`float` values (not booleans) and the
currencies USD, EUR, GBP, UAH. `parse_amount("12.50 usd")` returns the frozen
`CurrencyAmount(12.5, "USD")`; whitespace and currency case are normalised.
Invalid values raise `InvalidAmount`. Values remain floats for this spike,
not a claim of exact monetary arithmetic.

`format_amount(amount, decimal_places=2)` produces `"12.50 USD"`. Precision
must be an integer from 0 to 8. Standard Python numeric rounding is for display
only: a small positive amount can display as `"0.00 USD"`.

`sum_amounts([parse_amount("1 USD"), parse_amount("2 USD")])` returns
`CurrencyAmount(3.0, "USD")`. It accepts iterables, uses `math.fsum`, and rejects
empty input, mixed currencies, invalid items and numeric overflow.

`convert_amount(parse_amount("12.50 USD"), "EUR", rate=0.8)` returns
`CurrencyAmount(10.0, "EUR")`. The caller supplies a finite positive rate in
target units per source unit; there is no exchange-rate lookup. Source and
target currencies must be supported uppercase codes. Invalid rates, overflow
and a result that underflows to zero raise `InvalidAmount`.

Design reference: Mikko Ohtamaa's [finite-value JSON boundary fix](https://github.com/tradingstrategy-ai/web3-ethereum-defi/commit/382dbe6623bc79a6ed350139d3750ef75c09eb0b).
That upstream export maps non-finite metadata to null; our required amounts
reject it. This is an independent implementation of the boundary practice.
