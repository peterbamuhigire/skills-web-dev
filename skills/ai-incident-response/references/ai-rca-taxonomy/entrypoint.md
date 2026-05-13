> Consolidated from skills/ai-rca-taxonomy/SKILL.md into ai-incident-response on 2026-05-13. Load this through skills/ai-incident-response/SKILL.md, not as an active skill entrypoint.

# AI RCA Taxonomy
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Classifying the root cause of an AI incident.
- Categorising a postmortem and aggregating themes monthly.
- Auditing whether the engine's detection signals cover every RCA class.
- Designing engineering investment priorities from postmortem trends.

## Do Not Use When

- The task is the live response — `ai-incident-response-runbook`.
- The task is generic SaaS root-cause categorisation — `reliability-engineering` failure-mode catalogue.

## Required Inputs

- An incident or postmortem to classify (or a set, for aggregation).
- Optional: detection signal catalogue, for coverage audits.

## Workflow

1. Read this `SKILL.md`.
2. Pick the **primary class** from the taxonomy (§1) — exactly one.
3. Pick **contributing classes** — zero or more.
4. Apply the **reference patterns** (§2) to confirm the class fits.
5. Reach the **remediation playbook** (§3) per class.
6. Apply anti-patterns (§4).

## Quality Standards

- The taxonomy has exactly **one** primary class per incident (forces analytical clarity).
- Every class has at least one reference pattern with a real-world example.
- Every class has at least one remediation playbook.
- Taxonomy is reviewed quarterly; classes are added when ≥ 2 incidents in 6 months don't fit existing classes.
- Detection-signal coverage audit runs monthly: every class must have ≥ 1 detection signal in the catalogue or an explicit "currently uncovered" entry.

## Anti-Patterns

- Many primary classes per incident — defeats the purpose; aggregation becomes noise.
- New classes invented per incident — taxonomy bloats; aggregation impossible.
- Class label without a reference pattern — incidents claim the label but don't share root cause.
- Remediation playbook reduces to "monitor more" — not a remediation.
- Taxonomy lives in a wiki, not referenced in postmortems.

## Outputs

- Taxonomy YAML (canonical source).
- Reference patterns per class.
- Remediation playbooks per class.
- Monthly coverage audit report.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Taxonomy YAML | YAML | `ops/ai/rca-taxonomy.yaml` |
| Operability | Reference patterns | Markdown | `docs/ai/rca-patterns.md` |
| Operability | Coverage audit | Markdown | `audits/rca-coverage-2026-05.md` |

## References

- `references/taxonomy-and-patterns.md` — full taxonomy with reference patterns and remediation per class.
- Companion: `ai-incident-detection-and-triage`, `ai-incident-postmortem`, `ai-incident-response-runbook`, `ai-eval-harness`, `ai-prompt-injection-and-tenant-safety`, `ai-rag-multi-tenant`.

<!-- dual-compat-end -->

## §1 Taxonomy (Class List)

Seven top-level domains; classes within each. Each class id is `<domain>.<class>`.

### model
- `model.regression` — model output quality regressed.
- `model.deprecation` — provider has deprecated the model or label.
- `model.fine-tune-drift` — fine-tuned model drift from base.
- `model.distribution-shift` — production input distribution drifted vs train/eval.
- `model.system-message-rot` — system message stale vs current model behaviour.
- `model.prompt-regression` — prompt change caused regression.
- `model.prompt-drift` — prompt and model interplay drifted.

### retrieval
- `retrieval.index-drift` — index rebuild changed retrieval behaviour.
- `retrieval.chunk-quality-drift` — chunk shape drifted (length, encoding, language).
- `retrieval.embedding-model-change` — embedding model version changed.
- `retrieval.citation-drift` — answers cite chunks that no longer exist or have changed.
- `retrieval.tenant-isolation-bug` — per-tenant filters broken.

### tool-agent
- `tool.api-change` — vendor changed the tool API/contract.
- `tool.schema-change` — vendor changed the tool schema.
- `tool.vendor-outage` — vendor unavailable.
- `tool.indirect-prompt-injection` — tool output carries injection.
- `agent.action-scope-expansion` — agent took action outside approved scope.
- `agent.runaway-loop` — agent in a retry/tool loop.
- `agent.reversibility-mismatch` — action classified reversible was actually irreversible.

### eval
- `eval.test-set-rot` — goldens aged or no longer represent.
- `eval.judge-drift` — judge LLM diverges from humans.
- `eval.golden-set-leakage` — model has memorised goldens.
- `eval.missing-coverage` — no eval for the axis that broke.
- `eval.production-sampling-bias` — production sampling missed the failure mode.

### data
- `data.training-data-shift` — provider-side change in training data.
- `data.customer-data-evolution` — tenant content evolved (new shape, new language).
- `data.ingestion-drift` — ingestion pipeline produced different shape.
- `data.tenant-content-spike` — single-tenant content spike caused load/quality issues.

### infra
- `infra.gateway-routing-change` — gateway rule change re-routed unexpectedly.
- `infra.region-failover` — region failed over; binding changed.
- `infra.observability-gap` — incident was not diagnosable due to missing telemetry.
- `infra.rate-limit-misconfig` — internal rate limit misconfigured.

### commercial
- `commercial.provider-price-change` — provider changed price.
- `commercial.provider-rate-limit-change` — provider lowered rate limit.
- `commercial.contract-change` — contract clause activated.

### process
- `process.missed-release-gate` — gate skipped or missing.
- `process.deploy-without-canary` — change shipped past canary.
- `process.runbook-out-of-date` — runbook didn't reflect current system.
- `process.oncall-handoff-gap` — handoff lost context.

## §2 Reference Patterns

See `references/taxonomy-and-patterns.md` for one or more example patterns per class with:
- Symptom (what signal fires).
- Mechanism (what is actually going wrong).
- Distinguishing check (how to confirm this class vs adjacent).
- A short real-world example.

## §3 Remediation Playbooks

Each class points to remediation moves, both **mitigation** (in-the-moment) and **prevention** (engineering investment). Mitigations cross-link to `ai-incident-response-runbook/references/per-failure-class-playbooks.md`. Preventions cross-link to `ai-incident-postmortem/references/ai-action-items-catalogue.md`.

## §4 Anti-Patterns

- A class name without a clear distinguishing check vs adjacent classes. Cause: drift, miscategorisation.
- "process.human-error" — never a class. Always points to a missing gate or runbook.
- Taxonomy not versioned; old postmortems referenced by class names that no longer exist.
- Taxonomy expanded ad-hoc by individual postmortem authors. Add classes via review.


