> Consolidated from skills/ai-hallucination-slo-and-grounding/SKILL.md into ai-observability-and-debugging on 2026-05-13. Load this through skills/ai-observability-and-debugging/SKILL.md, not as an active skill entrypoint.

# AI Hallucination SLO and Grounding
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Setting a hallucination-rate SLO for a customer-facing AI feature (e.g., support copilot, AI search, RAG Q&A) so you can ship and operate it like any other reliability property.
- Designing citation / grounding UX — every claim links back to a source the user can verify.
- Tuning retrieval rerank cutoffs and "I don't know" thresholds so the assistant abstains rather than fabricates.
- Building the incident-response playbook when the hallucination error budget is burned in a window.

## Do Not Use When

- The task is the eval mechanics — `ai-eval-harness` (this skill *uses* the eval harness).
- The task is general AI safety / prompt injection — `ai-prompt-injection-and-tenant-safety`.
- The task is RAG mechanics — `ai-rag-multi-tenant` / `ai-rag-patterns`.

## Required Inputs

- Eval harness (`ai-eval-harness`) producing a faithfulness metric per request and per feature.
- Retrieval pipeline (`ai-rag-multi-tenant`) with reranker + score outputs.
- Product agreement on what counts as a hallucination (define before measuring).
- Observability stack (`observability-monitoring` + `ai-observability-and-debugging`).

## Workflow

1. Read this `SKILL.md`.
2. **Define hallucination** (§1) — the operational definition before any metric.
3. **Set the SLO** (§2) — target rate, window, error budget.
4. Implement **citation grounding** (§3) as a product surface, not a debug feature.
5. Tune **"I don't know" thresholds** and **rerank cutoffs** (§4) so the system abstains gracefully.
6. Wire the **error budget** (§5) into release decisions.
7. Build the **burn-rate alerting** (§6) and **incident response** (§7).
8. Apply anti-patterns (§8).

## Quality Standards

- Hallucination is defined in writing and the definition is stable.
- Faithfulness is measured continuously on production samples (1–5%).
- Every customer-facing AI answer includes citations the user can click through.
- Abstain rate is itself measured and budgeted — abstaining always > hallucinating.
- SLO breach freezes prompt/model changes (not the product).
- Incidents end with a regression row added to goldens.

## Anti-Patterns

- "Confidence score" displayed without grounding — meaningless.
- Citation always rendered as a footnote that customers never read. Make it inline.
- Threshold tuned to maximise "I answered" rate. Optimises for the wrong thing.
- SLO measured only on goldens, not on production. False sense of safety.
- Hallucination treated as a "model issue, not ours". The product owns the SLO.
- Single number for hallucination at the platform level; can't drill into a specific feature or tenant.

## Outputs

- Operational definition of hallucination for each feature.
- SLO + error-budget policy per feature.
- Citation / grounding UX patterns.
- Threshold table (rerank cutoff, abstain).
- Burn-rate alerts.
- Incident playbook.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Hallucination definition | Markdown | `docs/ai/hallucination-definition.md` |
| Release evidence | SLO policy | Markdown | `docs/ai/hallucination-slo.md` |
| UX | Citation patterns | Figma + markdown | `docs/ai/citation-ux.md` |
| Operability | Burn-rate alert config | YAML | `ops/alerts/hallucination-slo.yaml` |
| Operability | Incident playbook | Runbook | `docs/runbooks/hallucination-incident.md` |

## References

- `references/grounding-and-citation-ux.md` — design patterns + accessibility for citations.
- `references/slo-and-error-budget-math.md` — windowed SLO math + burn-rate alerts for AI.
- Companion: `ai-eval-harness`, `ai-rag-multi-tenant`, `ai-output-design`, `ai-prompt-injection-and-tenant-safety`, `ai-on-saas-architecture`, `observability-monitoring`, `reliability-engineering`.
- Incident handoff: a burn-rate alert is the **start** of an incident, not the end. See `ai-incident-detection-and-triage` for triage, `ai-incident-response-runbook` (failure class `hallucination-spike`) for first / second mitigations, `ai-incident-evidence-capture` for the evidence bundle, and `ai-incident-postmortem` for the postmortem. The burn-rate alert payload must include `runbook` link and `failure_class_hint: hallucination-spike`.

<!-- dual-compat-end -->

## §1 Operational Definition of Hallucination

Before measurement, write down what counts. Example for a support copilot:

> A response is a **hallucination** if it contains a non-trivial factual claim about the customer's product, policies, or data that is not supported by at least one retrieved citation (or by the system prompt content marked as authoritative).

Edges:
- Generic best-practice statements are not hallucinations (e.g., "you may want to check our docs").
- Reasonable rephrasing of cited content is not a hallucination.
- A correct claim with a wrong citation IS a hallucination (citation must support).
- A response that abstains is NOT a hallucination.

Definition lives in `docs/ai/hallucination-definition.md` and is referenced by the judge-LLM rubric.

## §2 The SLO

Per feature, define:

| Field | Example |
|---|---|
| SLI: hallucination rate | `judged_hallucinations / answered_responses` |
| Target | ≤ 2% over 28-day rolling window |
| Abstain SLO | abstain rate ≤ 8% (don't over-refuse) |
| Window | 28 days |
| Error budget | 0.02 × answered (e.g., 2,000 over 100k) |

Two SLOs — the hallucination one and the abstain one — keep the system honest. Push abstain rate to zero and you increase hallucinations.

## §3 Citation Grounding (Product Surface)

Citations are not a debugging feature; they are the product. Patterns:

- **Inline numeric markers** with hover/click to source.
- **Source preview** on hover — title, snippet, last-updated.
- **"Open source"** opens the doc at the cited section.
- **No citation? show "based on general knowledge"** with a lower confidence affordance.
- **Citation density** target: every paragraph with a factual claim must have ≥ 1 citation.

If the model cannot produce well-formed citations, the output is **post-processed**: claims are matched against retrieved chunks; unmatched claims are rewritten or removed; if too many are unmatched, the system abstains.

See `references/grounding-and-citation-ux.md`.

## §4 Thresholds for Abstaining

Two relevant thresholds:

1. **Rerank cutoff**: minimum reranker score for a chunk to be used. Below it, the chunk is dropped. If after filtering < N chunks remain, the system abstains.
2. **Confidence to answer**: derived from retrieval coverage of the question + judge-LLM confidence on grounding. Below threshold, abstain.

Tune by:
- Sweeping thresholds on a held-out set.
- Plotting hallucination rate vs abstain rate at each threshold.
- Picking the point on the curve that satisfies both SLOs with budget to spare.

Abstain copy patterns:
- "I couldn't find this in your knowledge base. Try rephrasing or [link a human]."
- Offers an escape hatch (human handoff, related articles).

## §5 Error Budget → Release Decisions

```
budget_remaining = SLO_target - observed_rate (over window)
```

Policy:
- Budget ≥ 50%: prompts/models can be deployed normally.
- Budget < 50%: only fixes; new prompts go through extra eval + canary.
- Budget < 20%: freeze prompt/model changes for the feature; root-cause review.
- Budget exhausted: feature put behind opt-in flag or downgraded to a safer (often slower) configuration.

This is the AI version of `reliability-engineering` SLO policy.

## §6 Burn-Rate Alerts

Multi-window:

| Window | Burn rate trigger | Severity |
|---|---|---|
| 1h | 14.4× | page on-call |
| 6h | 6× | page on-call |
| 24h | 3× | ticket + on-call awareness |
| 7d | 1× | manager review |

`14.4×` over 1h ≈ exhausts a 28d budget in 2 days. Standard SRE math, applied to faithfulness signal.

See `references/slo-and-error-budget-math.md`.

## §7 Incident Response

When budget is being burned:

1. **Investigate**: which feature, model, prompt version, tenant, retrieval state?
2. **Containment options**:
   - Rollback prompt to previous version.
   - Reduce rerank cutoff (more conservative).
   - Switch to a more grounded model.
   - Disable the affected feature for the affected tenant(s).
   - Kill-switch globally if scope unclear.
3. **Add a regression row** to `eval/goldens/.../regression.jsonl` for every reproducible failure.
4. **Post-mortem** including which threshold or definition needs tightening.
5. **Communicate** to affected tenants per their contract.

## §8 Anti-Patterns

- Citations rendered post-hoc by the UI without semantic matching — the model never saw them; they're decorative.
- Single confidence number instead of multi-dimensional (retrieval coverage + grounding score + format compliance).
- Tuning thresholds against goldens only; production has different distribution.
- Treating abstain rate as a failure — over-refusing is also a product failure.
- SLO with no consequence — no freeze, no review.
- Hallucination only measured by judge-LLM with no human spot-check. Judge drifts; product team needs to feel the metric.

## §9 Read Next

- `ai-eval-harness` — produces the SLI.
- `ai-rag-multi-tenant` — improves the retrieval inputs.
- `ai-output-design` — citation UX surface.
- `ai-feature-rollout-and-experimentation` — gates rollouts on this SLO.
- `ai-observability-and-debugging` — traces support root cause analysis.
- `reliability-engineering` — broader SLO discipline.


