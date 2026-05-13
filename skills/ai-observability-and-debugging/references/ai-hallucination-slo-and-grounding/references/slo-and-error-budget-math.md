# SLO and Error Budget Math — Reference

Applying standard SRE multi-window SLO math to hallucination rate.

## SLI

```
SLI_hallucination = judged_hallucinations / answered_responses     (per feature)
SLI_abstain       = abstained / total_user_requests
```

`answered_responses` excludes abstains. `judged_hallucinations` comes from production samples scored by judge-LLM (`ai-eval-harness`).

## SLO

Per feature, define a target SLO:

```
Target_hallucination ≤ 2%   over 28-day rolling window
Target_abstain       ≤ 8%
```

## Error budget

```
Budget_hallucinations = 0.02 × answered_in_window
Burn rate             = observed_hallucinations / Budget_hallucinations
```

A burn rate of 1× exhausts the budget exactly at window end. > 1× means budget will exhaust early.

## Multi-window burn-rate alerts

Standard Google SRE multi-window approach:

| Long window | Short window | Burn rate | Action |
|---|---|---|---|
| 1h | 5m | 14.4× | page on-call (fast burn) |
| 6h | 30m | 6× | page on-call |
| 24h | 2h | 3× | ticket + alert |
| 7d | 6h | 1× | manager review |

A burn-rate alert fires only when BOTH windows exceed the threshold — reduces noise.

`14.4×` over 1h exhausts a 28-day 2% budget in ~2 days at that rate.

## Implementation (Prometheus example)

Recording rules:

```yaml
groups:
- name: ai_slo
  rules:
  - record: ai_halluc_rate:1h
    expr: sum by (feature) (rate(ai_judged_hallucinations[1h]))
        / sum by (feature) (rate(ai_judged_responses[1h]))
  - record: ai_halluc_rate:6h
    expr: sum by (feature) (rate(ai_judged_hallucinations[6h]))
        / sum by (feature) (rate(ai_judged_responses[6h]))
  - record: ai_halluc_rate:24h
    expr: sum by (feature) (rate(ai_judged_hallucinations[24h]))
        / sum by (feature) (rate(ai_judged_responses[24h]))
```

Alert:

```yaml
- alert: HallucinationBudgetFastBurn
  expr: |
    (ai_halluc_rate:1h > 0.288)    # 14.4 × 0.02
    and
    (ai_halluc_rate:5m > 0.288)
  for: 5m
  labels: { severity: page }
  annotations:
    summary: "{{ $labels.feature }} hallucination rate burning budget at 14.4×"
```

## Per-tenant SLO

Optional but valuable for enterprise contracts:

- Compute per-tenant SLI.
- Enterprise contracts may include a per-feature, per-tenant SLO target.
- Per-tenant burn alerts feed into the customer-success on-call.

## Sample size

Production sample of 1–5% of traffic feeds the SLI. For low-volume features:
- Increase sample rate (up to 100%).
- Lengthen window (28d → 90d) to reduce noise.
- Combine with goldens-based SLI when production sample is too small.

## Calibration drift

If judge-LLM agreement with humans falls below 0.7 kappa, the SLI is no longer reliable. Recalibrate the judge before trusting alerts.

## Linking budget to release

In your CI / deploy system:

```python
budget_remaining_pct = compute_budget_remaining("support-copilot.answer", window="28d")
if budget_remaining_pct < 20:
    block_prompt_changes(feature="support-copilot.answer", reason="budget < 20%")
elif budget_remaining_pct < 50:
    require_extra_eval(feature="support-copilot.answer")
```

`ai-feature-rollout-and-experimentation` uses these signals to throttle rollouts.

## Anti-patterns

- One-window threshold ("alert if rate > 2%") — false positives on low-volume hours.
- Per-tenant alerting on tenants with < 100 daily requests — noise.
- Annual SLO — too slow to act on.
- SLI computed only from goldens — doesn't catch production-distribution issues.
- Budget that never affects shipping — discipline rots.
