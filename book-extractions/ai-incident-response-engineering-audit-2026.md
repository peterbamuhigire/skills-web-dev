# AI Incident Response & Postmortem Engineering Skills Audit — May 2026

**Lens:** Detect, triage, mitigate, communicate, recover, and postmortem **AI-specific** production incidents in a multi-tenant SaaS. Distinct from generic SaaS incident response because AI failure modes are silent, statistical, distributional, drift-based, jailbreak-based, and tool-chain-based — they need different detection signals, different mitigations, different evidence capture, different recovery patterns, and different RCA taxonomies than a 502-on-the-API outage.

**Inputs reviewed:** `ai-on-saas-architecture`, `ai-model-gateway`, `ai-hallucination-slo-and-grounding`, `ai-cost-per-tenant-attribution`, `ai-eval-harness`, `ai-observability-and-debugging`, `ai-prompt-injection-and-tenant-safety`, `ai-feature-rollout-and-experimentation`, `ai-agents-tools`, `reliability-engineering`, `saas-admin-backoffice-tooling`, `saas-control-plane-engineering`.

**Prior verdict (from the AI-on-SaaS SRS session):** the engine has solid AI architecture, eval, SLO, observability, and gateway skills, **but** there is no skill that owns the incident lifecycle for AI features. Hallucination SLO mentions burn-rate alerts; gateway mentions kill-switch; rollout mentions auto-rollback; observability mentions trace pull. These are puzzle pieces — there is no skill that puts them together as a runbook the on-call engineer reaches for at 02:14 when the hallucination rate is spiking. Generic `reliability-engineering` covers timeouts, retries, queue safety — it cannot help when a prompt regression silently halves the citation-accuracy of a copilot.

---

## Existing Incident-Related Coverage Audit

| Skill | Coverage today | Gap for AI incident response |
|---|---|---|
| `reliability-engineering` | Generic SRE: criticality classification, timeouts, retries, runbook template | Doesn't name AI failure classes; no AI-specific runbook; no AI evidence bundle. |
| `ai-hallucination-slo-and-grounding` | SLO definition, burn-rate alerts, freeze-on-breach | Stops at "page on-call" — no triage tree, no mitigation per failure class, no postmortem handoff. |
| `ai-cost-per-tenant-attribution` | Per-tenant cost capture, anomaly hooks | Anomaly hook is referenced but there is no incident-triage path for "cost runaway". |
| `ai-model-gateway` | Kill-switch contract (60s propagation), fallback chains, per-feature pin | Kill-switch surface exists but no playbook for *when* and *how* to flip; no documented model/prompt/index pin operations. |
| `ai-observability-and-debugging` | Trace per request, replay tooling, ticket→trace tie-back | No "trace bundle export" for an incident; no "show me everything from 14:32 for tenant X" mode. |
| `ai-feature-rollout-and-experimentation` | Auto-rollback on signal degradation | Rollback exists but stops at "flag flipped" — there is no handoff into an incident, no comms, no postmortem. |
| `ai-prompt-injection-and-tenant-safety` | Threat model + safety events + red-team | Safety events go to alerts; no jailbreak-incident response runbook; no regulator-notification path. |
| `ai-eval-harness` | Goldens, judge-LLM, eval drift | Eval drift is described as a signal — no incident path. |
| `ai-agents-tools` | ReAct loop, approval gates | No agent-action-incident path (irreversible action by an agent → who pages, what gets paused, what gets undone). |
| `saas-admin-backoffice-tooling` | Tenant ops, billing ops, audit log | No AI-incident console: no kill-switch button, no model-pin UI, no prompt-pin UI, no per-tenant-feature pause. |
| `saas-control-plane-engineering` | Audit log spine, tenant lifecycle | Doesn't classify AI-specific control-plane operations during an incident. |

---

## Cross-Cutting Gaps

1. **No AI-specific detection-signal catalogue.** Hallucination SLO burn, eval drift, cost anomaly, refusal spike, abstain-rate drop, citation-accuracy drop, retrieval-miss-rate, irreversible-action rate, tool-error-rate, latency p99 by stage, jailbreak-classifier hits — each one lives in a different skill, none classify as "this is a sev-1, page X within Y minutes."
2. **No severity matrix for AI incidents.** Severity is not the same as "API down". A silent hallucination at 4× the budget on the copilot used by the regulated-bank tenant is sev-1 even though the API returns 200 OK.
3. **No triage decision tree.** What do I check first? Is it the model (provider deprecation last night)? The prompt (deploy at 22:14)? The retrieval (index rebuild)? The judge (eval drift)? The agent (tool API change)? There is no documented branch order.
4. **No per-failure-class playbook.** Hallucination spike vs prompt drift vs model regression vs jailbreak vs cost runaway vs agent-action incident vs retrieval-drift vs training-data shift — each requires a different first move (model-pin vs prompt-rollback vs index-pin vs abstain-mode vs read-only-mode vs kill-switch). None of this is engineered.
5. **No AI evidence bundle spec.** When a postmortem is written next week, what state had to be captured *at the time of the incident*? Trace bundle, prompt+model+tool versions, retrieval set, eval-suite output, customer-affected list, action audit log, reproduce script, price table snapshot — none of this is named.
6. **No regulator-notification path.** EU AI Act Article 73 requires serious-incident reporting on high-risk AI systems within strict windows. No skill mentions it.
7. **No AI-specific postmortem template.** A generic postmortem template misses AI-specific RCA categories (judge drift, embedding-model change, golden-set leakage, indirect prompt injection, etc.).
8. **No AI RCA taxonomy.** The set of root causes for AI incidents is different from generic SaaS. There is no canonical catalogue.
9. **No recovery / re-promotion playbook.** After rolling back, how do we re-promote safely? Shadow-mode comeback, canary-during-recovery, eval-gated re-promotion — not encoded.
10. **No drill / game-day cadence.** Token-cost runaway, foundation-model deprecation, prompt-injection-via-tool, retrieval-poison, hallucination spike — none of these have rehearsed responses.

---

## NEW SKILLS (8)

| # | Skill | Purpose |
|---|---|---|
| 1 | `ai-incident-detection-and-triage` | Detection-signal catalogue, severity matrix (sev × tenant-scope × autonomy), triage decision tree, who-pages-whom, time-to-acknowledge targets. |
| 2 | `ai-incident-response-runbook` | First 5 / 30 / 120 minutes per failure class (8+ classes), mitigation moves (kill-switch, model-fallback, prompt-rollback, index-pin, abstain-mode, read-only-mode). |
| 3 | `ai-incident-evidence-capture` | Evidence bundle spec, chain-of-custody, reproduce-script template; one-command export at the time of incident. |
| 4 | `ai-incident-customer-comms` | Status-page templates per failure class, per-tenant notifications, per-severity escalation, EU AI Act Art. 73 regulator notification. |
| 5 | `ai-incident-postmortem` | Blameless AI postmortem template, AI-specific RCA categories, contributing-factor map, AI-specific action-items catalogue. |
| 6 | `ai-rca-taxonomy` | Full AI root-cause taxonomy: model / retrieval / tool / agent / eval / data / infra / commercial, each with reference patterns and remediation playbooks. |
| 7 | `ai-incident-recovery-and-rollback` | Rollback patterns (prompt-pin, model-pin, index-pin, tool-pin, gateway routing pin, full feature rollback); shadow-mode comeback; canary-during-recovery; eval-gated re-promotion. |
| 8 | `ai-incident-drill-and-game-day` | Game-day exercises (8+), drill cadence, success criteria, learnings flywheel, failure-mode rotation. |

---

## ENHANCEMENTS to existing skills

| Skill | Enhancement |
|---|---|
| `ai-hallucination-slo-and-grounding` | Add explicit "burn-rate-alert → incident-response handoff" with link to `ai-incident-response-runbook`. |
| `ai-cost-per-tenant-attribution` | Add "cost-anomaly → incident triage" cross-link with example alert payload. |
| `ai-observability-and-debugging` | Add "incident-mode" section: trace bundle export, "show me everything from 14:32 for tenant X", evidence-pack one-liner. |
| `ai-feature-rollout-and-experimentation` | Add "auto-rollback → incident" — rollback opens an incident automatically, not silently. |
| `ai-prompt-injection-and-tenant-safety` | Add "safety event → incident classification" with severity mapping. |
| `ai-model-gateway` | Add concrete kill-switch + fallback-chain + per-feature pin operator surfaces with code. |
| `ai-agents-tools` | Add "agent-action-incident" path: containment of in-flight agent tasks, undo windows, action-audit-log export. |
| `reliability-engineering` | Add pointer "for AI incidents see `ai-incident-response-runbook`" — do not duplicate the runbook. |
| `saas-admin-backoffice-tooling` | Add "AI incident console" requirement (kill-switch, model-pin, prompt-pin, index-pin, per-tenant-feature pause). |

---

## Reference Files (rich)

| Path | Purpose |
|---|---|
| `ai-incident-detection-and-triage/references/detection-signal-catalogue.md` | Every AI signal that can fire an incident, with thresholds, owners, and runbook links. |
| `ai-incident-detection-and-triage/references/severity-matrix.md` | Sev-1 / sev-2 / sev-3 / sev-4 rules with tenant-scope and autonomy axes. |
| `ai-incident-detection-and-triage/references/triage-decision-tree.md` | Ordered "what do I check first" branches per signal. |
| `ai-incident-response-runbook/references/first-five-first-thirty-first-two.md` | Universal first 5 / 30 / 120-minute playbook. |
| `ai-incident-response-runbook/references/per-failure-class-playbooks.md` | 8+ failure-class playbooks (hallucination spike, prompt drift, model regression, jailbreak, cost runaway, agent action, retrieval drift, training-data shift). |
| `ai-incident-evidence-capture/references/evidence-bundle-spec.md` | What's in the bundle, schema, retention. |
| `ai-incident-evidence-capture/references/chain-of-custody.md` | Who can read it, where it lives, how it's signed. |
| `ai-incident-evidence-capture/references/reproduce-script-template.md` | Generated script that re-runs the failing request offline. |
| `ai-incident-customer-comms/references/status-page-templates.md` | Status-page templates per failure class, language patterns. |
| `ai-incident-customer-comms/references/per-tenant-notification-templates.md` | Per-tenant DM templates per severity. |
| `ai-incident-customer-comms/references/regulator-notification-templates.md` | EU AI Act Art. 73 serious-incident, GDPR breach windows. |
| `ai-incident-postmortem/references/blameless-template.md` | Blameless AI postmortem markdown template. |
| `ai-incident-postmortem/references/ai-action-items-catalogue.md` | AI-specific action items (add golden, change eval gate, add red-team test, pin model, change prompt, etc.). |
| `ai-rca-taxonomy/references/taxonomy-and-patterns.md` | Full catalogue with examples and remediation. |
| `ai-incident-recovery-and-rollback/references/rollback-patterns.md` | Prompt-pin, model-pin, index-pin, tool-pin, gateway routing pin, full feature rollback. |
| `ai-incident-recovery-and-rollback/references/eval-gated-re-promotion.md` | Re-promotion gates and the "do not re-promote until X" rule set. |
| `ai-incident-drill-and-game-day/references/game-day-exercises.md` | 8+ rehearsed scripts. |
| `ai-incident-drill-and-game-day/references/drill-cadence.md` | Cadence, success criteria, rotation rules. |

---

## Cross-Engine Handoff

**To the SRS engine** (paired doc-side session): the engineering stack here produces the *tools, signals, evidence formats, code patterns, and operator surfaces*. SRS owns the *documents*: runbook spec (the markdown the on-call human reads), postmortem spec (template + required sections), severity-matrix doc (policy version, approved by leadership), regulator-notification policy doc. Both sides reference the same RCA taxonomy and severity matrix to stay in sync — recommend the SRS engine takes `ai-rca-taxonomy/references/taxonomy-and-patterns.md` and `ai-incident-detection-and-triage/references/severity-matrix.md` as the canonical source of truth and quotes them, not forks them.

**To agent engine:** when agent runtime skills land (per `agent-products-engineering-audit-2026.md`), the agent-action-incident path here should be extended to reference `ai-agent-runtime-architecture` containment surfaces.

**To compliance/legal engine:** EU AI Act Art. 73 serious-incident reporting, GDPR breach windows, sector regulator notifications need a legal review of the `regulator-notification-templates.md` per jurisdiction.

---

## Critical Gaps Remaining After This Stack

1. **No on-call rotation engineering.** Who is the AI on-call? Same as platform on-call? Separate? Pager schedule, handoff, ack SLA — not engineered. Suggest pairing with an `on-call-engineering` skill (future).
2. **No insurance / liability surface.** Some AI-incident-class events (irreversible agent action causing customer monetary loss) trigger an insurance claim path. Not in scope of engineering, but legal/finance need it.
3. **No customer-facing AI status surface.** Status page exists; an *AI-feature-specific* health page (per-feature SLO state, last-incident link, abstain rate today) is not engineered.

---

## Recommended Next Sessions

1. **`ai-on-call-engineering`** — paging, rotation, ack SLA, escalation, AI-specific on-call training. Pair with HR/people-ops.
2. **`ai-customer-facing-status-and-trust`** — per-feature health page, transparency report, AI trust center.
3. **`ai-model-deprecation-and-migration`** — the planned-incident class: provider deprecates a model, you have N weeks; this needs its own playbook (related to but distinct from incident response).
4. **`ai-third-party-vendor-incident-response`** — when the foundation-model provider has the incident, what's our side of the runbook?
