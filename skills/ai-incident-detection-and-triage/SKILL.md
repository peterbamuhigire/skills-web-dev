---
name: ai-incident-detection-and-triage
description: Use when designing detection and triage for AI-specific production incidents in a multi-tenant SaaS — the detection-signal catalogue (eval drift, hallucination SLO burn, cost anomaly, refusal spike, abstain-rate drop, citation-accuracy drop, retrieval miss-rate, irreversible-action rate, tool-error rate, latency p99), the severity matrix that combines sev × tenant scope × autonomy, and the triage decision tree that names what to check first per signal.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Incident Detection and Triage
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Wiring detectors that page on AI-specific signals (not just API 5xx).
- Defining the severity matrix for AI incidents in a multi-tenant SaaS.
- Building the triage decision tree the on-call engineer follows when paged at 02:14.
- Auditing existing alerts and finding the AI-specific gaps (hallucination silently spiking with 200 OK responses).

## Do Not Use When

- The task is the response itself — `ai-incident-response-runbook`.
- The task is the SLO definition — `ai-hallucination-slo-and-grounding`.
- The task is generic platform alerting — `reliability-engineering` and `observability-monitoring`.
- The task is the postmortem — `ai-incident-postmortem`.

## Required Inputs

- Eval harness emitting per-feature, per-variant metrics (`ai-eval-harness`).
- Hallucination SLO + burn-rate alerts (`ai-hallucination-slo-and-grounding`).
- Cost-per-tenant pipeline with anomaly hooks (`ai-cost-per-tenant-attribution`).
- AI trace schema (`ai-observability-and-debugging`).
- Safety event taxonomy (`ai-prompt-injection-and-tenant-safety`).
- Tenant tier list and which tenants are flagged as high-risk / regulated.

## Workflow

1. Read this `SKILL.md`.
2. Enumerate **detection signals** (§1) from the catalogue and decide which ones page.
3. Build the **severity matrix** (§2) — sev × tenant scope × autonomy.
4. Build the **triage decision tree** (§3) — what gets checked first per signal class.
5. Wire **paging routes** (§4) — who pages, time-to-ack target, escalation.
6. Define **time-to-classify** target (§5) — how long until a paged event becomes a classified incident with a class label.
7. Apply anti-patterns (§6).

## Quality Standards

- Every AI signal that can fire an incident has: a threshold, an owner, a runbook link, a severity rule.
- Severity is decided by the matrix, not the on-call engineer's gut.
- A paged on-call engineer reaches a classified failure class in < 10 minutes for sev-1 and < 30 minutes for sev-2.
- No silent failure class — if a class can happen, a detector exists, even if the threshold is approximate.
- Detection coverage is reviewed every quarter against the RCA taxonomy.

## Anti-Patterns

- "Latency and 5xx" alerts only — misses the entire AI-specific failure surface.
- One severity scale shared with platform — a hallucination spike on a regulated-bank tenant gets buried as sev-3 because the API returned 200.
- Page the model team for everything — exhausts the wrong rotation; the prompt team owns prompt drift, the data team owns retrieval drift.
- "Burn-rate alert" with no runbook link — paged engineer reaches a dashboard, not a playbook.
- Severity determined by customer escalation pressure rather than the matrix. Tier-1 customer screams, sev moves to sev-1 with no signal change — process collapses.
- No "time to classify" SLA — incidents drift unlabelled, postmortems can't aggregate.

## Outputs

- Signal catalogue with thresholds and runbook links.
- Severity matrix policy document.
- Triage decision tree per signal class.
- Paging route specification.
- Time-to-ack and time-to-classify targets.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | AI signal catalogue | Markdown + YAML | `ops/ai/signals.yaml` |
| Operability | Severity matrix policy | Markdown | `docs/ai/severity-matrix.md` |
| Operability | Triage decision tree | Mermaid + Markdown | `docs/ai/triage-tree.md` |
| Operability | Paging routes | YAML | `ops/ai/paging.yaml` |

## References

- `references/detection-signal-catalogue.md` — every AI signal, threshold, owner, runbook link.
- `references/severity-matrix.md` — sev × tenant-scope × autonomy with worked examples.
- `references/triage-decision-tree.md` — ordered "check this first" branches per signal class.
- Companion: `ai-incident-response-runbook`, `ai-hallucination-slo-and-grounding`, `ai-cost-per-tenant-attribution`, `ai-observability-and-debugging`, `ai-prompt-injection-and-tenant-safety`, `ai-eval-harness`, `ai-feature-rollout-and-experimentation`, `ai-rca-taxonomy`.

<!-- dual-compat-end -->

## §1 Detection Signals

Group signals by source. Every signal has: name, source, threshold, owner, runbook link, severity rule.

**Quality signals**
- Hallucination-rate burn (per feature, per tenant tier) — from `ai-hallucination-slo-and-grounding`.
- Citation-accuracy drop (per feature) — eval harness production sample.
- Abstain-rate drop (per feature) — abstain rate falling means the system answers more, hallucinates more.
- Refusal-rate spike — model refusing valid queries; usually points to provider-side change or safety classifier flapping.
- Eval-drift (golden suite) — daily eval suite score regression > N points.
- Judge drift — judge-LLM disagreement with humans on calibration set rises.

**Retrieval signals**
- Retrieval-miss rate (no relevant chunk found) — points at index drift, embedding-model change, chunk-quality drift.
- Top-K score collapse — top-K relevance scores fall — embedding regression or index corruption.
- Citation drift — answers cite chunks that no longer exist or have changed.

**Tool / agent signals**
- Irreversible-action rate (per tenant, per agent type) — agent doing more destructive things.
- Tool-error rate (per tool) — vendor outage or API change.
- Tool-schema-mismatch — agent-emitted tool call shape diverges from current schema.
- Action-approval bypass rate — agent finding ways around HITL.

**Safety signals**
- Jailbreak-classifier hit rate.
- PII-in-output rate.
- Cross-tenant-leakage classifier hits.
- Indirect-prompt-injection markers in tool outputs.

**Cost signals**
- Cost-anomaly per tenant (z-score over rolling window).
- Cost-anomaly per feature (total cost spike).
- Token-per-request p99 drift — prompt bloat or context-window misuse.
- Provider-rate-limit error rate.

**Performance signals**
- Latency p99 by stage (retrieval / gateway / provider / safety / post-processing).
- Time-to-first-token regression.
- Streaming abandonment rate.

See `references/detection-signal-catalogue.md` for full table.

## §2 Severity Matrix

Three axes:

| Axis | Values |
|---|---|
| Signal severity | quality degraded / quality breached / safety event / cost runaway / outage |
| Tenant scope | single tenant / one tier / one region / all tenants |
| Autonomy | suggestion-only / human-approves / agent-acts-irreversibly |

Examples:
- Hallucination burn on copilot, all tenants, suggestion-only → **sev-2** (quality, broad scope, low autonomy).
- Hallucination burn on copilot, regulated-bank tenant, agent-acts-irreversibly → **sev-1** (one tenant, but high autonomy + regulated = severity escalates).
- Cost-anomaly, single Free-tier tenant, suggestion-only → **sev-3** (containable).
- Cost-anomaly, all tenants, any autonomy → **sev-1** (runaway, money-bleeding).
- Confirmed jailbreak surfacing other-tenant data → **sev-1 always**.
- Agent took an irreversible destructive action outside approved scope → **sev-1 always**.

Full matrix and worked examples: `references/severity-matrix.md`.

## §3 Triage Decision Tree

The first branch is the **signal class**. Then under each class, the first three checks are documented in `references/triage-decision-tree.md`.

For example, "hallucination burn":
1. Was there a deploy in the last 24h? (Check the release log.) → prompt or model change → likely class: prompt drift / model regression.
2. Was there an index rebuild in the last 24h? → retrieval drift.
3. Was there a provider model update announced? → model regression.
4. Is the burn on one tenant or all? → tenant-specific (data shift) vs platform-wide.
5. Is the judge calibration drifting? → eval drift, not real regression.

Each branch ends in a **failure class label** that maps to a playbook in `ai-incident-response-runbook`.

## §4 Paging Routes

Route by signal class to the right rotation:

| Signal class | Primary rotation | Secondary |
|---|---|---|
| Hallucination / eval drift | AI-product on-call | AI-platform on-call |
| Retrieval drift | Data / retrieval on-call | AI-product |
| Model regression | AI-platform on-call | Vendor liaison |
| Cost runaway | AI-platform on-call | Finance partner |
| Jailbreak / safety | Security on-call | AI-product |
| Agent action | AI-product on-call | Customer success (for affected tenant) |
| Latency / 5xx | Platform on-call (generic) | AI-platform |

Time-to-ack: sev-1 ≤ 5 min, sev-2 ≤ 15 min, sev-3 ≤ 1h, sev-4 next business day.

## §5 Time-to-Classify

A paged event without a failure-class label is not an incident yet; it's a page. Target: classified within **10 minutes** for sev-1 and **30 minutes** for sev-2. The classification is one of the labels in `ai-rca-taxonomy`. If the on-call cannot classify within target, escalate; do not let the page languish.

## §6 Anti-Patterns

- A new AI feature ships without registering its signals in the catalogue.
- Severity decided per-incident by the responder; matrix exists but is not enforced in the runbook.
- Generic platform on-call gets paged for all AI signals — they don't have the context to triage.
- "Time-to-ack" tracked, "time-to-classify" not tracked — incidents look fast on paper, slow in reality.
- Signal threshold tuned to a level that *never* alerts. False sense of safety.
