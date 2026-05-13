---
name: ias-impairment
description: Impairment of non-financial assets under IAS 36 (full IFRS) and Section 27 (IFRS for SMEs). Indicator-based testing, recoverable amount (higher of fair value less costs of disposal and value in use), cash-generating units, goodwill impairment, reversal. Use when material PPE, intangibles, goodwill, or investment property carrying amounts could be impaired. Tier-3 scope — indicator-based reference built first; full annual-test machinery deferred until a goodwill-heavy or asset-intensive client demands it.
---

# Impairment of Assets (IAS 36 / Section 27)

## Tier-3 scope

For typical SME clients, impairment is indicator-driven and assessed annually as part of close. The full IAS 36 machinery (annual mandatory test of goodwill, cash-generating unit determination, value-in-use cash-flow projections with discount rates) becomes load-bearing for asset-intensive or M&A-active clients. Build the indicator-based assessment first; build full machinery when required.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/ifrs-for-smes-default.md` (Section 27)
- `doctrine/references/full-ifrs-overlay.md` (IAS 36)
- `doctrine/references/chart-of-accounts.md`

## Indicators

External:

- Significant decline in market value beyond normal use.
- Significant adverse changes in technology, market, economy, legal environment.
- Increase in market interest rates affecting discount rates.
- Carrying amount > market capitalisation (listed entities).

Internal:

- Obsolescence or physical damage.
- Plans to discontinue, restructure, or dispose of an asset.
- Worse-than-expected economic performance.

## Recoverable amount

= higher of:

- Fair value less costs of disposal.
- Value in use (PV of future cash flows from the asset / CGU).

## Carrying amount > recoverable amount → impairment loss

Recognised in P&L (or against revaluation surplus where applicable).

## Reversal

Section 27 / IAS 36 allow reversal of prior impairment (other than goodwill) up to the original carrying amount less subsequent depreciation, if indicators reverse.

Goodwill impairment is **not** reversed under either framework.

## Goodwill specifics

- Section 19 (IFRS for SMEs): goodwill amortised over useful life (max 10 years if useful life cannot be reliably estimated). Impairment tested on indicators.
- IFRS 3 (full IFRS): goodwill not amortised; tested for impairment annually.

## Build implications

- Indicator-assessment checklist run at each reporting date.
- Where indicator triggers, the system supports a workpaper for recoverable-amount calculation.
- Impairment journal posted via the posting service.
- Reversal journal where conditions met; goodwill impairments locked from reversal.
- Disclosure note generator.

## CoA implications

| Code | Name |
|---|---|
| 1799 Accumulated Impairment — PPE | Non-current contra. |
| 1899 Accumulated Impairment — Intangibles | Non-current contra. |
| 6750 Impairment Loss — PPE | P&L. |
| 6760 Impairment Loss — Intangibles / Goodwill | P&L. |
| 6770 Reversal of Impairment Loss | P&L (gain). |

## Forbidden patterns

- Reversal of goodwill impairment (blocker).
- Carrying amount > recoverable amount left unrecognised when indicator confirmed (blocker).
- Annual goodwill impairment test claimed under IFRS for SMEs (mis-application of frameworks).
- Discount rate hardcoded (use entity / asset-specific rate).

## Files

- `SKILL.md`.
- `references/indicator-checklist.md`.
- `references/value-in-use-workpaper-template.md` (build when first needed).

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
