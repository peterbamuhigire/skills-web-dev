# Forecasting Accuracy

A forecast is a promise with a confidence interval. The goal is not to be right every time — it is to be calibrated, so that leadership can plan hiring, cash, and investor conversations on real numbers.

## Category definitions

| Category | Confidence | Action |
|---|---|---|
| **Commit** | >90% this quarter | Will sign; procurement engaged; no open blockers |
| **Best case** | >50% this quarter | Plausible; some risk; clear path exists |
| **Pipeline** | Below best case, still real | Qualified but not yet committable |
| **Omitted** | <10% | Closed Lost or out-of-quarter |

Commit is a name staked. A rep who commits a deal and misses it twice in a row has a calibration problem, not bad luck.

## The forecast call — what a good call sounds like

```text
AE: "I'm committing Acme at $80k. Security review done Friday,
     MSA under legal, champion confirmed budget. Signing by the 25th."

Manager: "Economic buyer?"
AE: "CFO. Already agreed on price verbally. Champion sent CFO's
     approval email."

Manager: "Legal?"
AE: "Red-lines minor — indemnity cap. Their counsel said two business
     days. I'm comfortable."

Manager: "Commit. What's the downside if they miss the 25th?"
AE: "Slips to first week next quarter. No risk of loss."
```

Compare with a bad call:

```text
AE: "Acme should close this quarter. They're a strong deal, champion
     loves us."

Manager: "Economic buyer?"
AE: "Probably the CFO. Champion said he'd get approval."

Manager: "Legal?"
AE: "Haven't started."

Manager: "You're 40 days from quarter-end. Best case, not commit."
```

## Weighted pipeline vs committed-deal-list

Two parallel forecast methods; use both:

### 1. Committed-deal-list (bottom-up)

Sum the commit category in dollars. Manager applies a "manager adjustment" factor (typically 0.85-0.95x) based on historical commit accuracy.

### 2. Weighted pipeline (top-down sanity check)

Sum (ACV × stage-weight) across all active opportunities with close dates in the quarter. Compare to the committed-deal-list.

If the two methods differ by more than 20%, investigate — either the pipeline is too thin or the commits are optimistic.

## Accuracy measurement

For each quarter, measure:

- **Commit accuracy**: actual closed / committed (target 95-105%).
- **Best-case accuracy**: actual closed from best-case / best-case forecast (target 40-60%).
- **Slipped deals**: commits that slipped out-of-quarter (target <10% of committed count).
- **Surprise deals**: closed-won not in the forecast (acceptable small %; systematic means pipeline is not being captured).

Track per-rep, per-manager, per-segment. A rep with 70% commit accuracy is a coaching problem; a manager with 70% commit accuracy across their team is a process problem.

## Systematic biases and how to detect them

### Sandbagging

- Reps lowball commits to exceed easily.
- Signal: consistent commit accuracy >120%, attainment distribution clusters at 102-115%, best-case full of closed-wons.
- Fix: ask for commit + best-case; hold rep to both; coach transparency.

### Happy ears (optimism)

- Reps believe the buyer's vague timeline signals.
- Signal: commit accuracy <85%, deals slip repeatedly, close dates in the past.
- Fix: MEDDIC/SPICED discipline; require decision-process field (who signs, on what date, following what step).

### End-of-quarter stuffing

- Reps push deals to Closed Won aggressively in the last 10 days, some via discounting.
- Signal: >40% of quarter bookings in final 10 days; average discount spike in last week.
- Fix: deal desk gating on discount >20% in the final week; commission kicker for early-quarter close.

### "Nurture" as avoidance

- Reps park deals in a nurture stage rather than disqualify.
- Signal: growing nurture bucket with no age-out; no re-engagement outcomes.
- Fix: nurture deals age out after 60-90 days unless there is a new event.

## Pipeline coverage

Pipeline coverage = qualified pipeline entering the quarter / quarterly quota.

| Motion | Coverage target (start of quarter) |
|---|---|
| SMB | 3x |
| Mid-market | 3-4x |
| Enterprise | 4-5x |

If coverage is below target, the quarter is already at risk — stop worrying about forecast, start worrying about pipeline generation.

## Sample forecast review template (per rep)

```text
Rep: ____________                         Week: _____
Q target: £______      YTD closed: £______      Gap: £______

Commit (sum £____):
  Deal | ACV | Stage | Close date | Economic buyer | Champion | Next step
  ...

Best case (sum £____):
  Deal | ACV | Stage | Close date | Risk | Path to commit

Watch list (slipping or at risk):
  Deal | Reason | Action

Pipeline generation (next quarter):
  SQO created this week: _____
  Required weekly rate to hit 3x coverage: _____
```

## Cross-references

- `pipeline-stages.md` — exit criteria that make forecasts credible.
- `sales-ops-fundamentals.md` — rituals that surface forecast signal.
- `saas-business-metrics` — bookings, NRR, attainment roll-up.

## Anti-patterns

- Forecasting by gut — "I have a feeling about this one".
- Managers editing rep forecasts without feedback — reps lose calibration incentive.
- Single number forecasts — no uncertainty signal, no diagnostic value.
- Changing forecast definitions mid-year — destroys historical comparison.
- Treating forecast miss as a blame event rather than a learning event — reps will hide risk.
