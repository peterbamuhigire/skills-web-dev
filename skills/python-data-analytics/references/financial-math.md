# Financial Math

Currency math is `Decimal`. `float64` loses pennies, compounds the error, and eventually makes audit reconciliation impossible. Every function below keeps state in `Decimal` and only converts to `float` for plotting.

## Decimal setup

Set a process-wide precision and rounding mode once, at the entry point.

```python
from decimal import Decimal, getcontext, ROUND_HALF_UP

getcontext().prec = 28                    # 28 significant digits
getcontext().rounding = ROUND_HALF_UP     # banker's rounding elsewhere is a separate decision

CENTS = Decimal("0.01")
BPS   = Decimal("0.0001")
```

Helpers used across the functions below:

```python
def to_cents(x: Decimal) -> Decimal:
    return x.quantize(CENTS, rounding=ROUND_HALF_UP)

def dec(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))
```

Pass monetary values in as strings (`"1250.00"`) or `Decimal`, never as `float`.

## NPV

```python
def npv(rate: Decimal, cashflows: list[Decimal]) -> Decimal:
    """cashflows[0] is t=0. All items must be Decimal."""
    rate = dec(rate)
    total = Decimal("0")
    one_plus_r = Decimal("1") + rate
    factor = Decimal("1")
    for cf in cashflows:
        total += dec(cf) / factor
        factor *= one_plus_r
    return to_cents(total)
```

NPV sign convention: the initial investment is negative. `npv(Decimal("0.10"), [Decimal("-1000"), Decimal("400"), Decimal("400"), Decimal("400")])` equals `Decimal("-5.26")`.

## IRR

`numpy_financial.irr` works in float. For cents-accurate IRR, bisect in Decimal.

```python
def irr(cashflows: list[Decimal], tol: Decimal = Decimal("1e-7"), max_iter: int = 200) -> Decimal | None:
    cashflows = [dec(c) for c in cashflows]
    if not any(c < 0 for c in cashflows) or not any(c > 0 for c in cashflows):
        return None  # IRR requires at least one sign change

    lo, hi = Decimal("-0.999999"), Decimal("10")
    f_lo = npv(lo, cashflows)
    f_hi = npv(hi, cashflows)
    if f_lo * f_hi > 0:
        return None  # no sign change in bracket

    for _ in range(max_iter):
        mid = (lo + hi) / 2
        f_mid = npv(mid, cashflows)
        if abs(f_mid) < tol:
            return mid.quantize(Decimal("0.0001"))
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return mid.quantize(Decimal("0.0001"))
```

Production rules:

- IRR can have multiple solutions when cashflow signs change more than once. Document this with the user; consider MIRR for those cases.
- Always also return NPV at WACC; IRR in isolation misleads on scale.

## Amortisation schedule

Constant-payment mortgage / loan. Payment formula in Decimal:

```
pmt = P * r / (1 - (1 + r)^-n)
```

with `r` the periodic rate and `n` the number of periods.

```python
from decimal import Decimal

def amortization_schedule(
    principal: Decimal,
    annual_rate: Decimal,
    months: int,
    first_payment_date,
    currency: str = "UGX",
) -> list[dict]:
    P = dec(principal)
    r = dec(annual_rate) / Decimal("12")
    n = months

    if r == 0:
        pmt = to_cents(P / Decimal(n))
    else:
        one_plus_r_n = (Decimal("1") + r) ** n
        pmt = to_cents(P * r * one_plus_r_n / (one_plus_r_n - Decimal("1")))

    balance = P
    rows = []
    period_date = first_payment_date
    for i in range(1, n + 1):
        interest = to_cents(balance * r)
        principal_portion = to_cents(pmt - interest)
        if i == n:
            # flush rounding dust into the last payment
            principal_portion = balance
            pmt_this = to_cents(principal_portion + interest)
        else:
            pmt_this = pmt
        balance = to_cents(balance - principal_portion)
        rows.append({
            "period":      i,
            "date":        period_date,
            "payment":     pmt_this,
            "interest":    interest,
            "principal":   principal_portion,
            "balance":     balance,
            "currency":    currency,
        })
        period_date = _add_months(period_date, 1)
    return rows
```

The rounding-dust trick matters. Without it the final balance is off by a cent and auditors will flag it.

## Depreciation schedules

### Straight-line

```python
def straight_line(cost: Decimal, salvage: Decimal, life_years: int) -> list[Decimal]:
    annual = to_cents((dec(cost) - dec(salvage)) / Decimal(life_years))
    # distribute rounding dust into the last year
    years = [annual] * life_years
    total = sum(years, Decimal("0"))
    years[-1] = to_cents(years[-1] + (dec(cost) - dec(salvage) - total))
    return years
```

### Declining balance

```python
def declining_balance(cost: Decimal, salvage: Decimal, life_years: int, factor: Decimal = Decimal("2")) -> list[Decimal]:
    rate = factor / Decimal(life_years)
    book = dec(cost)
    sal = dec(salvage)
    out = []
    for _ in range(life_years):
        dep = to_cents(book * rate)
        if book - dep < sal:
            dep = book - sal
        out.append(dep)
        book -= dep
    return out
```

Declining balance stops at salvage value. Units of production depreciates per unit produced:

```python
def units_of_production(cost: Decimal, salvage: Decimal, total_units: int, units_by_period: list[int]) -> list[Decimal]:
    per_unit = (dec(cost) - dec(salvage)) / Decimal(total_units)
    return [to_cents(dec(u) * per_unit) for u in units_by_period]
```

## Day-count conventions

Interest accrual depends on the convention:

| Convention   | Days in month | Days in year | Typical use                    |
|--------------|---------------|--------------|--------------------------------|
| 30/360       | 30            | 360          | US corporate bonds, many loans |
| Actual/360   | actual        | 360          | Money market, USD LIBOR        |
| Actual/365   | actual        | 365          | GBP money market, UK gilts     |
| Actual/Actual| actual        | 365 or 366   | US Treasury bonds              |

```python
from datetime import date

def day_count_30_360(d1: date, d2: date) -> int:
    """US 30/360 convention."""
    day1 = min(d1.day, 30)
    day2 = 30 if (day1 == 30 and d2.day == 31) else d2.day
    return 360 * (d2.year - d1.year) + 30 * (d2.month - d1.month) + (day2 - day1)

def year_fraction(d1: date, d2: date, convention: str = "ACT/365") -> Decimal:
    if convention == "30/360":
        return Decimal(day_count_30_360(d1, d2)) / Decimal("360")
    if convention == "ACT/360":
        return Decimal((d2 - d1).days) / Decimal("360")
    if convention == "ACT/365":
        return Decimal((d2 - d1).days) / Decimal("365")
    if convention == "ACT/ACT":
        # simplified: use 366 if leap year contains either endpoint
        days = Decimal((d2 - d1).days)
        base = Decimal("366") if _contains_leap(d1, d2) else Decimal("365")
        return days / base
    raise ValueError(convention)
```

Accrued interest:

```python
def accrued_interest(principal: Decimal, annual_rate: Decimal, d1: date, d2: date, convention: str) -> Decimal:
    return to_cents(dec(principal) * dec(annual_rate) * year_fraction(d1, d2, convention))
```

## Compounding

```python
def future_value(principal: Decimal, rate: Decimal, years: Decimal, n_per_year: int = 1) -> Decimal:
    if n_per_year == 0:
        # continuous compounding: FV = P * e^(r*t)
        import math
        return to_cents(dec(principal) * Decimal(str(math.exp(float(rate * years)))))
    r_per = dec(rate) / Decimal(n_per_year)
    periods = Decimal(n_per_year) * dec(years)
    return to_cents(dec(principal) * (Decimal("1") + r_per) ** periods)
```

Rule of thumb:

- Daily compounding (n=365) is the common retail standard.
- Monthly compounding (n=12) aligns with most loans and subscriptions.
- Continuous compounding is rare outside derivatives; use it only when specified.

## Currency handling

Multi-currency invoices in a single report need a conversion strategy. Two common policies:

- **Transaction-date rate.** Convert each row on its invoice date using the FX rate from that date. Faithful to business reality; needs an FX-rates table keyed by `(currency, as_of_date)`.
- **Spot rate.** Convert every row at today's rate. Simpler but distorts historical comparisons.

Always document which the tenant has chosen, and store the choice. Store FX rates as `Decimal` with 6+ decimal places. Cross rates should be computed on load, not on the fly, to avoid order-of-multiplication errors.

Example FX merge:

```python
df = invoices.merge(
    fx_rates,
    left_on=["currency", "invoice_date"],
    right_on=["currency", "as_of_date"],
    how="left",
    validate="many_to_one",
)
assert df["rate"].notna().all(), "missing FX rate for some invoice dates"
df["net_reporting"] = df["net"].map(dec) * df["rate"].map(dec)
```

Three currency rules:

1. Never mix currencies in an aggregation without conversion. Sum of a UGX column and a USD column is meaningless.
2. Store both the original amount and the converted amount. Auditors and customer support both need them.
3. Show the FX rate used in the document footer of every exported report.

## Rounding policy

- Round money to 2 decimal places at recording time for most currencies; keep 4 decimals for intermediate computation.
- JPY, KWD, and a few others have different scales. Look up `ISO 4217` minor units; do not hardcode 2 dp.
- Rates and percentages: keep 6 decimals internally, round to 2-4 dp only on display.
- Banker's rounding (`ROUND_HALF_EVEN`) is statistically unbiased and preferred for accounting balances that are summed over many rows. Use `ROUND_HALF_UP` for consumer-facing invoices because it matches what people expect.

## Test vectors every financial function should have

- Zero rate: `npv(0, [-100, 50, 50])` equals `0` exactly.
- Zero horizon: amortisation with `months=0` raises a clear error.
- Sign flip: IRR of `[-100, 110]` equals `0.10` to four decimals.
- Rounding: amortisation rows sum to the original principal to the cent.
- Currency scale: JPY schedule has 0 decimal places; UGX has 0 on display but we still store 2 dp for rates.
