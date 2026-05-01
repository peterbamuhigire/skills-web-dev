# Quota and Commission Design

The comp plan tells reps what you actually care about, regardless of what the memo says. Design it to reward the outcomes you want (retention, new logos, expansion) and to self-correct when the plan produces bad deals.

## Terminology

- **OTE** (On-Target Earnings) = base + variable at 100% attainment.
- **Quota** = the number that pays 100% of the variable.
- **Attainment** = actual / quota.
- **Accelerator** = higher commission rate above 100% attainment.
- **Decelerator / threshold** = lower rate or zero below a floor (e.g., <50% attainment).
- **SPIF** (Sales Performance Incentive Fund) = short, targeted bonus for a specific behaviour.
- **Clawback** = commission reversed if the customer churns or fails to pay within a defined window.

## Base:variable ratios by role

| Role | Base : variable | Rationale |
|---|---|---|
| SDR / BDR | 60:40 or 70:30 | Behaviour-heavy, outcomes volatile; steady base keeps activity going |
| AE (SMB, mid-market, enterprise) | 50:50 | Balanced, industry norm, attainment drives the variable half |
| SE | 70:30 or 75:25 | Team contributor, not a closer; small variable tied to team attainment |
| CSM | 70:30 or 80:20 | Relationship-led; variable tied to NRR, renewal, expansion |
| AM | 60:40 | Commercial, renewal-owning; mix |
| Sales Manager | 60:40 | Tied to team quota, not personal selling |

## Quota sizing

Rule of thumb: AE quota = 4-6x OTE. Below 4x, the company overpays per dollar of ARR. Above 6x, top performers hit ceiling or churn.

- SMB transactional AE: 5-7x OTE (shorter cycles, more deals).
- Mid-market AE: 4-5x OTE.
- Enterprise AE: 3-5x OTE (longer cycles, higher uncertainty, fewer deals).

Target attainment distribution across the team:

- 65-75% of reps at or above quota.
- Top decile 150%+.
- Bottom quintile <50% (action list — coaching or exit).

If 100% of reps hit quota, quota is too low. If <40% hit quota, quota is too high or coverage / territory is broken.

## Accelerator structure

Standard shape:

```text
0%  - 49%   attainment: 0x commission rate (decelerator / threshold)
50% - 99%   attainment: 1.0x commission rate (linear)
100% - 150% attainment: 1.5x rate (first accelerator)
150%+       attainment: 2.0x rate (double accelerator)
```

Rationale: reps crossing 100% should feel a clear boost; a flat plan caps the motivation of the top 20% who actually build the year.

## SPIFs

Use sparingly (2-3 per year) to push one behaviour. Examples:

- **New-logo SPIF**: £500 per new logo for the next 60 days.
- **Multi-year SPIF**: 0.5x base commission on multi-year upfront deals.
- **Product-X SPIF**: flat $1k per deal attaching a newly launched product.
- **Q1 ramp SPIF**: to fight slow January starts, pay 2x on deals closed in first 30 days.

SPIF rule: pay on provable, unambiguous criteria, in under 60 days, and never let them accumulate.

## Clawbacks

Clawback protects against reps closing bad-fit deals that churn immediately.

- **Standard**: commission fully clawed back if customer churns within 90 days of going live.
- **Graduated**: 100% claw in 0-90 days, 50% in 91-180 days, 0% thereafter.
- **Non-payment clawback**: if the customer never pays, commission is reversed.

Only enforceable if commission is paid on cash collected (see below) or held in escrow for the claw window.

## Cash collected vs bookings

| Basis | Cash flow fit | Rep behaviour signal |
|---|---|---|
| On bookings (signed order) | Harder on cashflow (you pay before you receive) | Faster pay, simpler plan |
| On invoice (billed) | Middle ground | Standard for annual-upfront |
| On cash collected | Best cashflow fit | Aligns rep with collections; discourages risky credit |

Recommendation for most SaaS: commission on invoice for annual-upfront contracts; commission on cash for monthly or deferred billing. Always add a clawback on churn.

## Worked plan examples

### SMB AE (ACV $3k-$10k, SaaS)

```text
OTE: $120k (60k base, 60k variable)
Quota: $600k new ARR
Commission rate: 10% of ARR (60k / 600k)
Threshold: commission starts at 40% attainment
Accelerators: 1.5x over 100%, 2.0x over 150%
Clawback: 100% on churn <90 days
SPIF: $300 per new logo, unlimited
```

### Enterprise AE (ACV $100k+, SaaS)

```text
OTE: $300k (150k base, 150k variable)
Quota: $1.5M new ARR
Commission rate: 10% of ARR
Threshold: 50% attainment
Accelerators: 1.5x over 100%, 2.0x over 150%; extra 0.25x kicker for multi-year
Clawback: 100% on churn <180 days; 50% on non-payment
Pay: on invoice, with 15% held for 180 days
```

### CSM (book $2M ARR)

```text
OTE: $130k (100k base, 30k variable)
Variable components:
  - 40% on gross retention (target 95%)
  - 40% on net retention (target 110%)
  - 20% on expansion ARR booked (target $200k)
Accelerators on NRR above 115%
No clawback; churn already deducts from the NRR measure
```

## Governance

- **Plan doc**: written, versioned, signed by CRO and CFO. No verbal plans.
- **Dispute process**: reps raise commission disputes within 30 days of payment; ops responds within 10 business days.
- **Change control**: plans change at fiscal year or quarter boundaries, not mid-cycle.
- **Transparency**: reps can see their attainment and commission accrual in near-real-time; surprises kill trust.

## Cross-references

- `saas-business-metrics` — CAC payback is directly affected by commission structure.
- `subscription-billing` — invoice timing drives commission payout timing.
- `software-pricing-strategy` — discount policy and approval thresholds interact with comp.

## Anti-patterns

- Plans that pay on booked ARR with no clawback — reps close non-retaining deals.
- Complex plans with >3 components — reps cannot optimise; they pick one and ignore the rest.
- Changing plan mid-year without grandfathering — destroys trust and makes reps hedge.
- Paying CSMs on NPS alone — they avoid hard conversations.
- No decelerator below 50% — keeps underperformers on salary with no urgency.
