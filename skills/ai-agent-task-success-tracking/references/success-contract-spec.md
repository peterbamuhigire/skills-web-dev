# Success Contract — Schema and Examples

A success contract is a per-feature, versioned declaration of what "resolved" means.

## Schema

```yaml
feature: <string>                # required; must match agent feature catalogue
version: <YYYY-MM>               # required; bump when definition changes
resolution_definition: <text>    # one paragraph, customer-readable
hard_signals:                    # ALL must be false for resolution
  - <expression>
soft_signals_required:           # ALL must be true for resolution
  - <name>: <evaluator>          # evaluator = literal | heuristic | judge
judge_prompt: <prompt_ref>       # registry reference if any soft signal uses judge
human_verification_sample_rate: <float 0..1>
human_verification_full_when:
  - <expression>
billing_treatment_on_resolved: <enum: full | partial(<frac>) | none>
billing_treatment_on_attempted_unresolved: <enum: full | partial(<frac>) | none>
intervention_billing_treatment:  # what if HITL intervened?
  light: <enum>
  heavy: <enum>
ttr_target_p50_seconds: <int>
ttr_target_p95_seconds: <int>
notes: <free text>
```

## Versioning Rules

- `version` is monotonically increasing (YYYY-MM).
- A contract version is **immutable** once a verdict has been produced under it.
- Migrating to a new version: all *new* tasks judge under the new contract; *in-flight* tasks finish under their original.
- Daily rollups carry a `contract_version` column so dashboards stay consistent.

## Worked Examples

### support_copilot

```yaml
feature: support_copilot
version: 2026-05
resolution_definition: >
  The customer received a response that materially addressed the
  problem in the original ticket, and the ticket was not re-opened
  within 72 hours by the same customer.
hard_signals:
  - state in ['FAILED','BUDGET_EXCEEDED','KILLED','ABANDONED']
  - off_script_irreversibles > 0
  - final_response_empty: true
  - final_response_says_cannot_help: heuristic
soft_signals_required:
  - addresses_intent: judge
  - no_reopen_within_72h: heuristic (waits up to 72h; otherwise tentative)
judge_prompt: prompt://judges/support-resolution.v3
human_verification_sample_rate: 0.05
human_verification_full_when:
  - tenant.sla_class == 'bespoke'
  - judge_confidence < 0.70
billing_treatment_on_resolved: full
billing_treatment_on_attempted_unresolved: partial(0.10)
intervention_billing_treatment:
  light: partial(0.85)     # agent did most of it
  heavy: partial(0.30)     # human did most of it
ttr_target_p50_seconds: 60
ttr_target_p95_seconds: 180
notes: |
  - "Resolved" requires the customer not to re-open. Tentative verdict
    until 72h passes; final verdict written then.
  - For shadow-tested intent classes, full human verification overrides.
```

### log_investigator

```yaml
feature: log_investigator
version: 2026-04
resolution_definition: >
  A root cause was identified, supporting evidence cited from the logs
  examined, and either a fix PR was opened or a ticket created with
  remediation steps.
hard_signals:
  - state in ['FAILED','BUDGET_EXCEEDED','KILLED','ABANDONED']
  - off_script_irreversibles > 0
  - cited_evidence_count < 2
soft_signals_required:
  - root_cause_stated: heuristic
  - remediation_artifact_created: heuristic   # PR id or ticket id present
  - addresses_user_question: judge
judge_prompt: prompt://judges/log-investigator-resolution.v2
human_verification_sample_rate: 0.10
human_verification_full_when:
  - tenant.sla_class == 'bespoke'
  - judge_confidence < 0.70
billing_treatment_on_resolved: full
billing_treatment_on_attempted_unresolved: partial(0.20)   # exploration has some value
intervention_billing_treatment:
  light: partial(0.85)
  heavy: partial(0.40)
ttr_target_p50_seconds: 300
ttr_target_p95_seconds: 1800
```

### code_change_agent

```yaml
feature: code_change_agent
version: 2026-03
resolution_definition: >
  A pull request was opened, passed CI, was reviewed and merged by a
  human, and was not reverted within 7 calendar days.
hard_signals:
  - state in ['FAILED','BUDGET_EXCEEDED','KILLED','ABANDONED']
  - off_script_irreversibles > 0
  - pr_opened: false
  - pr_passed_ci: false
  - pr_merged: false
soft_signals_required:
  - merged_pr_not_reverted_within_7d: heuristic  # tentative until 7d
  - addresses_task_intent: judge
judge_prompt: prompt://judges/code-change-resolution.v2
human_verification_sample_rate: 0.05
human_verification_full_when:
  - tenant.sla_class == 'bespoke'
billing_treatment_on_resolved: full
billing_treatment_on_attempted_unresolved: none   # PR not merged = no value
intervention_billing_treatment:
  light: partial(0.85)
  heavy: partial(0.20)
ttr_target_p50_seconds: 1800
ttr_target_p95_seconds: 7200
notes: |
  - "Reverted within 7 days" hard-disqualifies. Tentative verdict at
    merge; final at +7 days.
  - "PR closed without merge" -> unresolved. Customer cannot be billed
    for unmerged code.
```

## Tentative vs Final Verdicts

Some signals require a wait (no-reopen-within-72h, not-reverted-within-7d). The pipeline writes a *tentative* verdict immediately for billing UX (the dashboard shows it as "pending confirmation") and a *final* verdict after the wait.

Billing waits for *final* unless the contract opts into tentative billing (rare; explicit). SLA breach detection uses *final*. Both verdicts share the same `task_id`; the verdict row is updated, not appended, and a `final_decided_at` column is set.

## Customer-Visible Wording

The `resolution_definition` text appears verbatim on the customer SLA dashboard next to the resolution-rate number. The customer must be able to read this and recognize the bar they paid for.

Bad wording: "The agent did a good job."
Good wording: "We solved the customer's problem and they did not re-open the ticket within 72 hours."

## Migrating a Contract

When you bump version:

1. Open a PR with the new YAML and a migration note in `CHANGELOG.md`.
2. Run the new judge prompt against the last 30 days of production traces; compare verdict distribution.
3. If verdict distribution shifts > 3pp, hold the PR; the new contract is materially harder/easier.
4. After review, ship to one tenant cohort first (e.g., Pro non-bespoke), measure for 14 days, then ramp.

Never silently retune the judge or heuristic without a version bump. Auditors will ask which contract was in effect on day X.
