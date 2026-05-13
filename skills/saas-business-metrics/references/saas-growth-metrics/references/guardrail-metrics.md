# Guardrail Metrics

Source: Okonkwo, *Growth Engineering* (Wiley, 2025), Chapters 8 and 10.

## What a guardrail metric is

Every experiment has two metric classes:

- **Success metric** — the thing you are trying to move (signups, revenue per user, feature adoption).
- **Guardrail metric** — the thing that must NOT move adversely. A treatment that wins on the success metric but breaks a guardrail is a ship blocker, not a winner.

A guardrail is not a "secondary metric" or a "nice to monitor" metric. It is a hard gate. The PM owns defining both classes in the experiment spec **before** the experiment launches. Declaring guardrails after results arrive is cherry-picking.

## The standard guardrail set

Every experiment in a SaaS product should pair the success metric with at least the following guardrails. Define the specific threshold per product.

| Guardrail | Typical threshold | Rationale |
|---|---|---|
| P95 page latency | no increase greater than 5% | slow pages reduce revenue and increase bounce |
| Error rate (5xx, JS exceptions) | no increase greater than 10% | silent regressions leak quality |
| Crash rate (mobile) | no increase | crashes destroy trust and ratings |
| Revenue per session | no decrease greater than 2% | protects monetisation while moving activation |
| Support ticket volume | no increase greater than 15% | a confusing feature creates support cost that offsets wins |
| Core feature usage (for adjacent features) | no decrease greater than 5% | cannibalisation check |
| 7-day retention delta | no decrease | short-term lift must not harm stickiness |

Thresholds are product-specific. Set them with the team before launch; do not negotiate them down under commercial pressure after the experiment reads negative on a guardrail.

## Platform-level guardrails (cross-experiment)

Some guardrails apply at the platform level, not per experiment:

- Sample ratio mismatch (SRM) — chi-squared on assignment counts; fail if p < 0.01
- Event ingestion lag — fail if lag greater than 10 minutes during the experiment window
- Experiment assignment stability — no user flipped between variants
- Duplicate counting — no event recorded more than once per trigger

These should run as automated checks in the experiment scorecard job, not as manual reviews.

## Guardrail review workflow

1. PM writes guardrails into the experiment spec at proposal time.
2. Data scientist sizes the experiment so guardrails are also statistically detectable at their threshold.
3. During the run, guardrails are monitored daily. A breach during the run can justify an early stop.
4. At scorecard time, the decision is: success hit AND all guardrails within bounds → ship. Success hit AND a guardrail breached → do not ship; re-design.
5. If a guardrail is breached only marginally (within noise of the threshold), flag it for a follow-up experiment; do not silently ship.

## Anti-patterns

- Declaring guardrails after results (cherry-picking).
- Treating guardrails as "metrics to watch" with no ship gate.
- No latency or error-rate guardrail on a feature that ships new queries or rendering.
- A guardrail with no pre-declared threshold — "monitor it" is not a guardrail.
- Removing a guardrail after a breach to justify the ship (never do this — either the guardrail was wrong, which must be formally changed pre-launch for the next experiment, or the treatment actually failed).

## See also

- `skills/experiment-engineering/SKILL.md` — the engineering discipline of trustworthy experiments.
- `skills/experiment-engineering/references/experiment-spec-template.md` — where guardrails sit in the spec.
