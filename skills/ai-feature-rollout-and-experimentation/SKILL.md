---
name: ai-feature-rollout-and-experimentation
description: Use when rolling out AI features safely in a multi-tenant SaaS — feature flags scoped per tenant/user, percentage rollouts gated by eval and SLO budget, canary cohorts, A/B testing of prompts/models, automatic rollback on quality regression, tenant-level opt-out and consent, and shadow-mode for risky changes.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Feature Rollout and Experimentation
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Launching a new AI feature or a major prompt/model change.
- A/B testing two prompts or two models on live traffic with statistical rigor.
- Rolling out gradually by tenant tier, region, or cohort.
- Adding tenant-level opt-out/consent surfaces required by enterprise procurement.
- Automating rollback when an SLO or eval signal degrades.

## Do Not Use When

- The task is the eval harness itself — `ai-eval-harness`.
- The task is product-level prompt design — `ai-prompt-engineering`.
- The task is generic feature flagging unrelated to AI — use your flag platform docs.

## Required Inputs

- Feature-flag platform (LaunchDarkly, Statsig, ConfigCat, Unleash, in-house).
- Eval harness producing per-feature, per-variant metrics.
- SLO + error budget signals (`ai-hallucination-slo-and-grounding`).
- Tenant tier + consent state.

## Workflow

1. Read this `SKILL.md`.
2. Define the **rollout taxonomy** (§1) — internal → dogfood → canary → tier ramp → GA.
3. Wire **flags + targeting** (§2) — per-tenant, per-user, per-cohort, per-region.
4. Build **shadow-mode** capability (§3) for risky changes.
5. Implement **A/B + multivariate** evaluation (§4) with eval harness integration.
6. Wire **auto-rollback on signal degradation** (§5).
7. Provide **tenant-level opt-out and consent** (§6).
8. Document **release runbook** (§7).
9. Apply anti-patterns (§8).

## Quality Standards

- No AI prompt or model change goes to GA without staged rollout.
- Every variant has a primary metric and a guardrail metric.
- Auto-rollback triggers in < 10 minutes after a guardrail breach.
- Tenant opt-out is honoured at the gateway, not the UI.
- Consent is captured per tenant per AI feature class; recorded with timestamp + actor.
- Every rollout has a release log entry with start time, stages, metrics, decisions.

## Anti-Patterns

- One global flag → on for everyone. No early-warning blast radius.
- A/B with one metric and no guardrail. Optimises one thing, breaks another.
- Manual rollback only. Slow at 3am.
- Tenant opt-out implemented as a UI hint that doesn't actually disable the model call.
- Shadow-mode that compares only on a tiny sample. Confidence is illusion.
- "Soft launch" with no rollout plan. Six tenants find a critical bug at the same time.

## Outputs

- Rollout taxonomy specification.
- Flag and targeting policy.
- Shadow-mode runner code.
- A/B experiment design template.
- Auto-rollback rules and alert wiring.
- Tenant consent / opt-out surface.
- Release runbook template.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Rollout plan per change | Markdown | `docs/ai/rollouts/<change>.md` |
| Release evidence | A/B experiment design | Markdown + JSON | `docs/ai/experiments/<exp>.md` |
| Operability | Auto-rollback rules | YAML | `ops/alerts/ai-rollback.yaml` |
| Compliance | Consent records | DB rows | `tenant_ai_consents` table |

## References

- Companion: `ai-eval-harness`, `ai-hallucination-slo-and-grounding`, `ai-cost-per-tenant-attribution`, `ai-on-saas-architecture`, `ai-observability-and-debugging`, `deployment-release-engineering`, `saas-entitlements-and-plan-gating`.
- Incident handoff: an auto-rollback is the **opening** of an incident, not a silent revert. The rollback action must (a) flip the flag, (b) open an incident in the incident tracker with `failure_class_hint` derived from the breaching guardrail, (c) page the AI on-call. See `ai-incident-detection-and-triage` for severity, `ai-incident-response-runbook` for the playbook, and `ai-incident-recovery-and-rollback` for the eval-gated re-promotion path that brings the new variant back safely.

<!-- dual-compat-end -->

## §1 Rollout Taxonomy

Five stages, each with entry/exit criteria.

| Stage | Audience | Entry | Exit |
|---|---|---|---|
| Internal | platform team | CI green, goldens green | 24h no critical issues |
| Dogfood | all staff tenants | internal pass | 48h faithfulness ≥ target |
| Canary | 1–3 friendly tenants | dogfood pass + their consent | 1 week SLO holds |
| Tier ramp | Free → Starter → Pro → Business → Enterprise | canary pass | each tier 1 week SLO holds |
| GA | all entitled tenants | tier ramp complete | n/a |

Per-tenant overrides allow flagship customers to opt into earlier stages.

## §2 Flags + Targeting

Flag identity:

```
ai.<feature>.<change-id>           # e.g., ai.support-copilot.prompt-v18
```

Targeting rules in order:
1. Per-tenant force-on / force-off list (operator override).
2. Per-tenant consent state — must be opt-in for opt-in features.
3. Stage cohort (Internal / Dogfood / Canary / Tier).
4. Region (if regional gating).
5. Percentage rollout within cohort.

Resolved at the gateway *before* binding lookup so the binding (model, prompt version) can be variant-specific.

## §3 Shadow Mode

Risky changes (new model, new prompt, new retrieval) ship first in **shadow**:

- Real traffic goes to the existing variant; the new variant runs in parallel.
- Both outputs scored (judge-LLM) and stored.
- No user-facing change.

Implementation: gateway, after producing the primary response, asynchronously calls the shadow variant; logs both. Pairs are scored offline.

Promote shadow → canary when distribution metrics match within tolerance and judge-LLM prefers the new variant on ≥ 55% of pairs (with significance).

## §4 A/B + Multivariate

Design template:

```yaml
experiment_id: support-copilot.prompt.v18-vs-v17
hypothesis: "v18 improves faithfulness by ≥ 2pp without regressing latency"
metric:
  primary: faithfulness                       # higher is better
  primary_min_uplift: 0.02
  primary_significance: 0.05
guardrails:
  - name: latency_p95
    threshold: { max: 3500 }
  - name: cost_per_generation
    threshold: { max: 0.02 }
  - name: abstain_rate
    threshold: { max: 0.10 }
audience:
  stages: [canary, tier:starter, tier:pro]
  region: any
allocation: { v17: 50, v18: 50 }
min_sample: 5000 per variant
max_duration: 14 days
```

Decision after `min_sample` is met:
- Primary uplift significant AND no guardrail breach → promote v18.
- Primary uplift not significant → hold v17.
- Guardrail breach in any window → rollback v18 immediately.

Use a sequential-testing-aware library (e.g., Bayesian or sequential alpha-spending) — peeking penalty matters for online AI evals.

## §5 Auto-Rollback

Rules engine that watches a variant's metrics:

```yaml
- variant: support-copilot.prompt-v18
  rules:
    - condition: faithfulness_1h < 0.92
      action: pause_rollout
    - condition: faithfulness_6h < 0.90
      action: rollback
    - condition: abstain_rate_1h > 0.20
      action: rollback
    - condition: cost_p95_1h > 0.05
      action: pause_rollout
    - condition: ai.injection.suspected_rate_1h > baseline*3
      action: rollback
```

`pause_rollout` stops ramping; `rollback` flips the flag back. Both record an event and an in-product notice (if visible).

## §6 Tenant Consent and Opt-Out

Two contracts:

- **Opt-in features** (e.g., agent that takes actions, training-data contributions): tenant admin explicitly toggles on. Default off.
- **Opt-out features** (e.g., the support copilot itself): default on; tenant admin can turn off.

Schema:

```sql
CREATE TABLE tenant_ai_consents (
    tenant_id   BIGINT UNSIGNED NOT NULL,
    feature_class VARCHAR(64) NOT NULL,       -- 'agent', 'training_data', 'support_copilot'
    state       ENUM('opt_in','opt_out','unset') NOT NULL,
    actor_user_id BIGINT UNSIGNED,
    set_at      DATETIME NOT NULL,
    PRIMARY KEY (tenant_id, feature_class)
);
```

Gateway reads consent before honoring flags. Consent state is independent of entitlement state (Enterprise plan with consent = unset → still off until set).

## §7 Release Runbook

Per change, a markdown doc:

```
# Rollout: support-copilot prompt v18

Owner: @pb
Start: 2026-05-12 09:00 UTC
Stages: Internal → Dogfood → Canary → Pro → GA
Variant: support-copilot.prompt-v18 vs v17
Hypothesis: ...
Risk: ...
Rollback plan: flag flip; LD link

## Log
- 2026-05-12 09:00 — Internal 100%
- 2026-05-13 09:00 — Dogfood 100%; faithfulness +1.8pp; no guardrails
- 2026-05-15 09:00 — Canary acme/globex; faithfulness +2.1pp
- ...
```

## §8 Anti-Patterns

- "We flipped it for everyone." No diagnostics on regression.
- Auto-rollback rule that triggers on a single bad minute. Noise → flapping.
- Shadow comparisons that include tenants who consented to v17 only.
- Opt-in features turned on by default for trial tenants. Procurement disaster.
- Consent stored only in the marketing tool, not in the gateway. Honoured nowhere.
- One experiment per quarter — culture problem.
- No release log; next person can't reason about why the prompt is what it is.

## §9 Read Next

- `ai-eval-harness` — produces the metrics.
- `ai-hallucination-slo-and-grounding` — guardrail signals.
- `ai-cost-per-tenant-attribution` — cost guardrail.
- `ai-observability-and-debugging` — investigation in flight.
- `deployment-release-engineering` — broader release discipline.
- `saas-entitlements-and-plan-gating` — overlap with entitlements.
