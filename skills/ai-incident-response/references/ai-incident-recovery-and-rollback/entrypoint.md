> Consolidated from skills/ai-incident-recovery-and-rollback/SKILL.md into ai-incident-response on 2026-05-13. Load this through skills/ai-incident-response/SKILL.md, not as an active skill entrypoint.

# AI Incident Recovery and Rollback
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- An incident has been contained via a mitigation primitive and the question is "how do we get back to normal safely?"
- Designing the rollback / re-promotion contract between incident response and engineering.
- Auditing whether last quarter's incidents actually re-promoted cleanly.

## Do Not Use When

- The task is the live response — `ai-incident-response-runbook`.
- The task is the postmortem — `ai-incident-postmortem`.
- The task is the rollout in general (non-incident) — `ai-feature-rollout-and-experimentation`.

## Required Inputs

- Active mitigation primitive (model-pin, prompt-pin, etc.) currently in effect.
- Evidence bundle with failing-request samples.
- Eval harness, golden suite, and the option to add the incident's regression to goldens.
- Feature-flag platform with stage-based rollout.

## Workflow

1. Read this `SKILL.md`.
2. Identify the **rollback pattern** in effect (§1).
3. Decide the **recovery strategy** (§2) — leave-pinned, shadow-mode comeback, or eval-gated re-promotion.
4. Define the **re-promotion gates** (§3) — what must be true before un-pinning.
5. Run **shadow-mode comeback** (§4) if appropriate.
6. Run **canary-during-recovery** (§5) — slower than normal canary; constrained tenants.
7. Run **eval-gated re-promotion** (§6) — automated gates that block un-pinning.
8. Close out (§7) — incident closes only when re-promotion is complete or the rollback is documented as the new permanent state.
9. Apply anti-patterns (§8).

## Quality Standards

- Recovery has a written plan with named gates and a named owner, attached to the incident.
- Every rollback either re-promotes within an agreed window (e.g., 2 weeks) or is made permanent by an engineering decision logged in the postmortem.
- Re-promotion does not bypass the original release gates; it adds incident-specific gates on top.
- Shadow-mode comeback is the default for any model, prompt, or retrieval rollback that was caused by a quality regression.
- A regression golden is added before re-promotion attempts begin.
- No silent "we just un-pinned it on Friday afternoon" — every step is logged.

## Anti-Patterns

- Rollback becomes permanent by accident — no engineering decision, no plan, no review, just nobody un-pinned it.
- Re-promotion at 17:00 Friday; nobody on-call for the weekend.
- Re-promotion skipping canary because "this is the same change as before".
- No regression golden added — same incident recurs on the next attempt.
- Re-promotion gated only on eval suite; production sample not checked.
- "Recovery" treated as the on-call's job, not the feature team's; ownership unclear.

## Outputs

- Recovery plan per incident.
- Re-promotion gate checklist.
- Shadow-mode runner config.
- Canary-during-recovery configuration.
- Decision log entry per rollback (re-promote vs make permanent).

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Recovery plan | Markdown | `recovery/inc-1923-plan.md` |
| Operability | Re-promotion gate result | YAML | `recovery/inc-1923-gates.yaml` |
| Operability | Shadow-mode results | JSON | `recovery/inc-1923-shadow.json` |
| Operability | Decision log | Markdown | `recovery/inc-1923-decision.md` |

## References

- `references/rollback-patterns.md` — every rollback pattern with exact ops and verification.
- `references/eval-gated-re-promotion.md` — gates, shadow-mode comeback, canary-during-recovery, decision flow.
- Companion: `ai-incident-response-runbook`, `ai-incident-postmortem`, `ai-feature-rollout-and-experimentation`, `ai-eval-harness`, `ai-hallucination-slo-and-grounding`, `ai-model-gateway`.

<!-- dual-compat-end -->

## §1 Rollback Patterns in Effect

See `references/rollback-patterns.md` for full taxonomy. Summary:

| Pattern | What's pinned | How to un-pin | Re-promotion lens |
|---|---|---|---|
| prompt-pin | prompt version | gateway prompt pin removed | A/B old-vs-new prompt; shadow first |
| model-pin | model version | gateway model pin removed | A/B old-vs-new model; shadow first |
| index-pin | retrieval index snapshot | retrieval pin removed | A/B old-vs-new index on retrieval+answer eval |
| tool-pin / tool-disable | tool version or "off" | re-enable; pin to new version | tool contract test green first |
| gateway routing pin | routing rule | revert routing rule | provider health stable; eval on both providers |
| full feature rollback | flag variant | flag variant re-enabled | full rollout taxonomy again |

## §2 Recovery Strategy

Choose one:

1. **Leave-pinned (make permanent)** — the rollback is the right long-term state. Document in postmortem; remove the "incident-pin" label; close the open rollback row.
2. **Shadow-mode comeback** — run the new version in shadow alongside the pinned version; promote when shadow eval meets criteria.
3. **Eval-gated re-promotion** — fix the issue (PR, new prompt, new model), then re-promote through staged rollout with incident-specific gates.

Decision criteria:

- If the new version had a fundamentally wrong axis (broke abstain-vs-fabricate): strategy 3 with a fix.
- If the new model is a regression with no fix path (provider's problem): strategy 1 until provider fixes.
- If the new prompt is broadly correct but had one bad case: strategy 2 (shadow) after adding the regression to goldens.

## §3 Re-Promotion Gates

Default gates (in addition to the standard release gates):

- **Regression golden green.** The exact failing pattern is in the golden suite and the new version passes it.
- **Shadow window green.** Shadow run produced equal-or-better outputs vs pinned version for N requests (default 1,000) over W hours (default 24h).
- **Eval suite at parity or better.** No regression on any subset > threshold.
- **Cost neutral.** Tokens-per-request not > 10% worse than pinned.
- **Time-since-incident ≥ floor.** Default: 48h since incident close (1 week if sev-1 with data implications).
- **On-call coverage.** Re-promotion only during business hours of the primary on-call's time zone; never on-call-less days.

Gates are encoded:

```yaml
# recovery/inc-1923-gates.yaml
incident_id: inc-1923
re_promotion_target: prompt-v19  # new prompt with fix
gates:
  - regression_golden_green:
      golden_id: abstain-vs-fabricate-2026-05
      required: pass
  - shadow_window_green:
      duration_hours: 24
      min_requests: 1000
      pass_rate_floor: 0.96
  - eval_suite_parity:
      subset_max_regression_pp: 1.0
  - cost_neutral:
      tokens_per_request_max_increase_pct: 10
  - time_floor:
      hours_since_close: 48
  - on_call_coverage:
      window: business_hours
      excluded_days: [friday-pm, weekends]
status: pending
gate_results: {}
```

A gate-runner job evaluates these and emits a pass/fail; the feature flag system can be configured to read the gate-runner status before promoting.

## §4 Shadow-Mode Comeback

Reuses `ai-feature-rollout-and-experimentation` §3 (shadow-mode). Specifics for recovery:

- Shadow target = the new candidate (prompt-v19, model X+1, index Y+1).
- Comparator = the pinned version (prompt-v17 in effect).
- Sample = stratified by tenant tier; include the affected tenant set.
- Duration ≥ 24h, ≥ 1,000 requests.
- Outputs scored by judge and human-spot-check (≥ 50 samples).
- Result captured in `recovery/inc-1923-shadow.json` with per-axis breakdown.

## §5 Canary-During-Recovery

When shadow passes, canary begins. Constraints vs normal canary:

- **Smaller cohort first**: 1 internal tenant only (24h).
- **Then 1–3 friendly tenants** (consent confirmed; 1 week).
- **Then 5% of the affected tier** (1 week).
- **Then resume normal tier ramp**.

Auto-rollback rules from `ai-feature-rollout-and-experimentation` apply. Additionally: any re-fire of the original signal during canary triggers immediate rollback and reopens the incident.

## §6 Eval-Gated Re-Promotion (Flow)

```
gate_runner --inc inc-1923 \
            --gates recovery/inc-1923-gates.yaml \
            --output recovery/inc-1923-result.json

if all_gates_pass:
    flag_platform set ai.support-copilot.prompt = v19 --stage canary
else:
    notify owner; do not promote
```

The flag platform reads `gate_runner` status before applying the stage change; manual override requires AI-lead approval and logs a decision-log entry.

## §7 Close-Out

The incident closes when:
- Re-promotion is complete to GA, **or**
- A decision-log entry documents the rollback as the new permanent state, **or**
- The feature is decommissioned.

The incident does **not** close while a rollback is in effect with no plan. Open incidents have weekly review with AI leadership until closed.

## §8 Anti-Patterns

- "Tested it locally, looks fine, un-pinning it now" — bypasses gates.
- Re-promotion to GA in one step after recovery — same blast radius as before.
- Shadow with a too-small sample — false confidence.
- Same eval suite that missed the original regression — re-promotion gate has the same blind spot.
- Recovery plan owned by the IC who responded, not the feature team — implementation drift.
- Decision log absent for "permanent rollback" — six months later, nobody knows why we're on the old version.


