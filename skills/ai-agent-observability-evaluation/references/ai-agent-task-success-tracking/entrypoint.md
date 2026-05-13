> Consolidated from skills/ai-agent-task-success-tracking/SKILL.md into ai-agent-observability-evaluation on 2026-05-13. Load this through skills/ai-agent-observability-evaluation/SKILL.md, not as an active skill entrypoint.

# AI Agent Task Success Tracking
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Engineering the **production verdict pipeline** that says, for every finished task, whether it was a real resolution.
- Defining **per-feature success contracts** — what counts as "resolved" for support-copilot, log-investigator, code-change-agent.
- Wiring the **heuristic → LLM-judge → human-verification** cascade for cost-tiered scoring.
- Building **per-tenant resolution-rate dashboards** and the underlying daily rollup tables.
- Building the **dispute resolution flow** when a customer claims a task wasn't resolved (or claims it was, when we say it wasn't).
- Producing the **evidence pack** that backs every billed-as-completed task or every SLA-credit-issued breach.

## Do Not Use When

- The task is golden-set / pre-production eval — `ai-agent-eval`.
- The task is the **commitment** layer (what SLA we publish) — `ai-agent-sla-and-commitments`.
- The task is **issuing the credit** when breach is detected — `ai-agent-sla-credit-automation`.
- The task is hallucination-specific grounding signal — `ai-hallucination-slo-and-grounding`.

## Required Inputs

- Agent runtime emitting `agent.task.completed` events with trace IDs (`ai-agent-runtime-architecture`).
- Trace + tool-I/O store (`ai-agent-observability-and-replay`).
- Pre-production goldens to calibrate the judge (`ai-agent-eval`).
- LLM gateway with a cheap judge model pinned (`ai-model-gateway`).
- Human-verification workforce or in-tenant approver inbox.
- Per-feature success-contract spec (from product). See `references/success-contract-spec.md`.

## Workflow

1. Read this `SKILL.md`.
2. Write the **success contract** per feature (§1). See `references/success-contract-spec.md`.
3. Implement the **judge cascade** (§2). See `references/judge-cascade-pipeline.md`.
4. Persist the **verdict and evidence** (§3) on the task row.
5. Roll up to **per-tenant daily / 30d rates** (§4).
6. Wire **dispute resolution** (§5). See `references/dispute-resolution.md`.
7. Wire the **verdict → billing gate** (§6) — only `success_verdict = true` counts as completed.
8. Apply anti-patterns (§7).

## Quality Standards

- Every terminal-state agent task gets a verdict within 5 minutes (heuristic tier) or 30 minutes (judge tier) or 4 business hours (human tier).
- Heuristic tier handles ≥ 70% of tasks (cheap path); judge tier the next ~25%; human tier the last ~5%.
- Judge-LLM agreement with humans ≥ 80% on the sampled audit set; re-calibrate quarterly.
- Every verdict has an `evidence_ref` (trace ID + judge prompt version + judge response + heuristic decisions). Disputes resolve from this in < 30 minutes.
- Daily rollup tables (`agent_resolution_daily`) are recomputable from raw verdicts; a re-run produces identical output.
- Verdicts are **idempotent on `(task_id, judge_pipeline_version)`** — re-running the cascade yields the same row.
- Production verdict drift vs. golden-set eval is monitored; > 5pp delta opens an investigation.

## Anti-Patterns

- Treating `state == 'COMPLETED'` as success. That is the runtime's own claim; the agent decided. We need an independent verdict.
- Single LLM-judge call on every task — expensive, slow, and slow to reproduce.
- Verdict stored as a boolean with no evidence reference. Disputes become "trust us".
- Heuristic-only pipeline. Cheap is fine; cheap-and-wrong is litigation.
- Judge model is the same model as the agent. Tautology.
- Customer-disputes flow that lacks a rebuttal path — first claim wins, vendor pays.
- No drift monitor. Production verdicts silently diverge from goldens; SLA dashboards lie.

## Outputs

- Per-feature success contract (Markdown + YAML).
- Judge-cascade pipeline (Python).
- `task_success_verdicts` schema + daily rollup.
- Dispute resolution runbook + UI.
- Verdict → billing-gate integration spec.
- Drift monitor + alert rules.

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Architecture | Success contract per feature | YAML + Markdown | `docs/sla/success-contracts.md` |
| Release evidence | Judge calibration report | Markdown | `docs/sla/judge-calibration-2026Q2.md` |
| Operability | Drift monitor dashboard | Dashboard link | `docs/sla/dashboards/verdict-drift.md` |
| Compliance | Dispute resolution log | DB | `task_success_disputes` |

## References

- `references/success-contract-spec.md` — schema and worked examples per feature class.
- `references/judge-cascade-pipeline.md` — heuristic → LLM-judge → human pipeline with code.
- `references/dispute-resolution.md` — customer dispute + rebuttal flow.
- Companion: `ai-agent-eval`, `ai-agent-observability-and-replay`, `ai-agent-runtime-architecture`, `ai-agent-sla-and-commitments`, `ai-agent-attempted-vs-completed-billing`, `ai-hallucination-slo-and-grounding`, `ai-model-gateway`.

<!-- dual-compat-end -->

## §1 Success Contracts per Feature

A success contract answers: *what counts as resolved for this feature?*

```yaml
feature: support_copilot
version: 2026-05
resolution_definition: >
  The customer received a response that addressed the ticket and the
  ticket was not re-opened within 72 hours.
hard_signals:                # if any of these is true, NOT resolved
  - state in ['FAILED','BUDGET_EXCEEDED','KILLED','ABANDONED']
  - off_script_irreversibles > 0
soft_signals_required:       # all must be true for resolution
  - final_response_present: true
  - final_response_addresses_intent: judge
  - no_user_reopen_within_72h: heuristic
judge_prompt: prompt://judges/support-resolution.v3
human_verification_sample_rate: 0.05    # 5% spot check
human_verification_full_when:
  - tenant.sla_class == 'bespoke'
  - judge_confidence < 0.7
  - feature.flag('shadow_quality_eval') == true
billing_treatment_on_resolved: full
billing_treatment_on_attempted_unresolved: 0.10 * full   # see attempted-vs-completed skill
```

Full schema and per-feature examples in `references/success-contract-spec.md`.

## §2 The Judge Cascade

Three tiers, ordered cheapest first:

```
[HEURISTIC]  →  [LLM JUDGE]  →  [HUMAN VERIFY]
   ~70%             ~25%             ~5%
   <100ms           ~3s              hours
   $0               ~$0.005          $0.50+
```

### Tier 1: Heuristic

Deterministic rules per feature. Examples:
- `support_copilot`: if state == COMPLETED and final response > 80 chars and no user reopen within 72h → resolved.
- `log_investigator`: if root cause identified and PR/ticket linked → resolved.
- `code_change_agent`: if PR merged and not reverted in 7 days → resolved.

Heuristics emit a verdict + confidence. Confidence < threshold → cascade.

### Tier 2: LLM Judge

Cheap pinned model. Prompt registry, versioned. Reads task trace + final response + customer follow-up.

```python
def judge_task(task_id: int, contract: SuccessContract) -> JudgeVerdict:
    bundle = build_judge_bundle(task_id)    # trace, final_response, customer_followups
    prompt = prompt_registry.get(contract.judge_prompt)
    resp = gateway.call(
        feature="success_judge",
        model_pin="claude-x-cheap-pinned-v1",   # cheap judge, versioned
        prompt=prompt,
        inputs=bundle,
        max_tokens=500,
        seed=task_id,                            # deterministic where supported
    )
    return JudgeVerdict(
        verdict=resp.json["resolved"],
        confidence=resp.json["confidence"],
        rationale=resp.json["rationale"],
        prompt_version=prompt.version,
        model_pin=resp.model_pin,
        judge_request_id=resp.request_id,
    )
```

Confidence < threshold → cascade to human.

### Tier 3: Human

Routed to a queue. SLA: 4 business hours. Reviewer sees the task viewer + judge rationale + decides resolved / not-resolved / cannot-determine.

Full implementation in `references/judge-cascade-pipeline.md`.

## §3 Verdict Schema

```sql
CREATE TABLE task_success_verdicts (
  task_id              BIGINT PRIMARY KEY,
  tenant_id            BIGINT NOT NULL,
  feature              VARCHAR(64) NOT NULL,
  verdict              ENUM('resolved','unresolved','indeterminate') NOT NULL,
  tier                 ENUM('heuristic','judge','human') NOT NULL,
  confidence           DECIMAL(4,3) NULL,
  heuristic_signals    JSON NULL,
  judge_prompt_version VARCHAR(64) NULL,
  judge_model_pin      VARCHAR(64) NULL,
  judge_rationale      TEXT NULL,
  judge_request_id     VARCHAR(64) NULL,
  human_reviewer_id    BIGINT NULL,
  human_decided_at     DATETIME NULL,
  evidence_ref         VARCHAR(128) NOT NULL,    -- trace ID + signed bundle
  pipeline_version     VARCHAR(64) NOT NULL,
  created_at           DATETIME(3) NOT NULL,
  UNIQUE (task_id, pipeline_version),
  INDEX (tenant_id, feature, created_at)
);
```

`evidence_ref` resolves to a signed bundle (trace, judge prompt + response, human decision if any). Bundles retained ≥ 7 years for regulated tenants.

## §4 Per-Tenant Rollups

```sql
CREATE TABLE agent_resolution_daily (
  tenant_id        BIGINT NOT NULL,
  feature          VARCHAR(64) NOT NULL,
  day              DATE NOT NULL,
  attempted_count  INT NOT NULL,
  resolved_count   INT NOT NULL,
  intervened_count INT NOT NULL,
  irreversibles_offscript INT NOT NULL,
  ttr_p50_seconds  INT NOT NULL,
  ttr_p95_seconds  INT NOT NULL,
  PRIMARY KEY (tenant_id, feature, day)
);
```

Backfilled by a daily job (with re-run safe windows for late-arriving human verifications, default 7 days).

The 30d view:

```sql
CREATE OR REPLACE VIEW agent_resolution_30d AS
SELECT tenant_id, feature,
       SUM(attempted_count)            AS attempted,
       SUM(resolved_count)             AS resolved,
       SUM(resolved_count) / NULLIF(SUM(attempted_count), 0) AS rate,
       SUM(intervened_count)           AS intervened,
       SUM(intervened_count) / NULLIF(SUM(attempted_count), 0) AS intervention_rate,
       SUM(irreversibles_offscript)    AS offscript_count
FROM agent_resolution_daily
WHERE day >= CURRENT_DATE - INTERVAL 30 DAY
GROUP BY tenant_id, feature;
```

This view powers SLA breach detection.

## §5 Dispute Resolution

A customer can dispute a verdict in either direction:
- "You said resolved, but the agent did not solve my problem." (Refund / re-do request)
- "You said unresolved, but it was resolved." (Rare — usually an SLA-credit dispute.)

Flow:

1. Dispute filed (in-product or via support).
2. System pulls the evidence bundle.
3. Human reviewer (1 level up from automated tier) re-decides.
4. If reviewer overturns: verdict updated, billing/credit adjusted, audit row written.
5. If reviewer upholds: rebuttal returned to customer with rationale.
6. Escalation path: ombudsman / external arbitrator (Enterprise contracts only).

Disputes per tenant per period are capped (anti-abuse). See `references/dispute-resolution.md`.

## §6 Verdict → Billing Gate

The pipeline emits `agent.resolution.completed` only when `verdict='resolved'`. Billing skill consumes this event, not the runtime's `agent.task.completed`.

```
agent.task.completed (runtime claim)
        │
        ▼
  judge cascade
        │
        ▼
verdict='resolved'? ── no ──→ agent.resolution.unresolved (attempted-only billing)
        │ yes
        ▼
agent.resolution.completed (full billing)
```

See `ai-agent-attempted-vs-completed-billing`.

## §7 Anti-Patterns

- Runtime state == success. Tautology.
- Always-judge pipeline. Burns money on obvious cases.
- Heuristic-only pipeline. Cheap and wrong.
- Judge model == agent model. Encodes the same biases.
- Verdict stored without `evidence_ref`. Disputes become trust battles.
- Late-arriving human verifications mutate old rollup days without a versioned re-run.
- Drift between production and goldens is never alerted. Silent regression of the gate.
- Customer disputes pile up; no per-tenant cap; vendor pays everyone who asks.


