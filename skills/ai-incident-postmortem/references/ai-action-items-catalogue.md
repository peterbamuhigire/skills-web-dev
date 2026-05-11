# AI Postmortem Action-Items Catalogue

Action items must be **concrete**, **AI-specific**, **owned**, and **verifiable**. This catalogue lists action-item *kinds* per RCA class, with example phrasings. A real action item picks a kind and binds it to the incident's specifics.

## Schema

```
id          : POSTMORTEM-action.kind.subkind
category    : e.g., eval.add-golden
description : single-sentence concrete action
owner       : person (not team)
due         : ISO date
verification: observable change in the world that proves "done"
linked_inc  : inc-<id>
```

## Model — actions

- `model.pin` — Pin <feature> to dated model `<provider>/<model>@<date>`; remove `*-latest`.
  Verification: trace `model_version` label matches the pinned value 100% of the time.
- `model.fallback-chain-revisit` — Re-rank fallback chain after eval comparing primary vs fallback on goldens.
  Verification: chain order updated; eval results in release log.
- `model.shadow-canary-on-version` — Run a shadow canary on the new model version when provider announces a new release; promote only after N days green.
  Verification: shadow runner active; release log shows N-day evaluation.

## Prompt — actions

- `prompt.add-golden` — Add golden cases covering the axis moved by the failing prompt change.
  Verification: golden suite includes the new subset; suite shows expected pass/fail on incident's prompt versions.
- `prompt.diff-eval-gate` — Require eval pass on prompt diff before merge.
  Verification: CI fails on a regression PR.
- `prompt.version-pin-policy` — Disallow merging a prompt change without a deploy plan and a rollback note.
  Verification: PR template enforces; lint check exists.

## Retrieval — actions

- `retrieval.index-pin` — Pin <feature> to index snapshot `<id>`.
- `retrieval.embedding-pin` — Pin embedding model version explicitly; remove auto-track.
- `retrieval.chunk-quality-monitor` — Add chunk-length / chunk-quality distribution monitor; alert on drift > 20%.
- `retrieval.citation-validator` — Add a citation-resolves-to-current-chunk check; alert on dangling citations.

## Tool / Agent — actions

- `agent.action-classification` — Reclassify action `<X>` from reversible → irreversible (or vice versa) based on observed harm.
- `agent.approval-gate-add` — Move action `<X>` from auto-execute to human-approve.
- `agent.tool-version-pin` — Pin tool `<name>` to version `<v>`; remove latest pointer.
- `agent.indirect-injection-defense` — Sanitise tool outputs before they re-enter the model context.
- `agent.action-budget` — Cap actions per task/per tenant/per session at a defined number.

## Safety — actions

- `safety.red-team-add` — Add captured jailbreak prompt(s) to the red-team suite.
- `safety.classifier-tighten` — Tighten input/output classifier threshold for pattern <X>.
- `safety.deny-list-add` — Add patterns <list> to gateway input deny-list.
- `safety.creds-rotate` — Rotate credentials potentially exposed in the incident.
- `safety.threat-model-update` — Update threat model for <feature> with the new attack vector.

## Eval — actions

- `eval.add-axis` — Add a new evaluation axis (e.g., abstain-vs-fabricate) to the suite.
- `eval.judge-recalibrate` — Re-calibrate judge against humans on a fresh calibration set.
- `eval.golden-refresh` — Refresh goldens that have leaked (judge has memorised) or aged.
- `eval.production-sampling-tune` — Adjust production sampling rate / stratification to better detect class.
- `eval.release-gate-tighten` — Add a new metric (e.g., abstain-rate-drop) as a release-blocking gate.

## Data — actions

- `data.shape-monitor` — Add a data-shape monitor for ingestion (e.g., new content types in <feature>).
- `data.ingestion-validate` — Add validation step in ingestion pipeline for <issue>.
- `data.tenant-content-isolation-check` — Verify per-tenant content filters end-to-end on a fresh fixture.

## Infra — actions

- `infra.region-failover-test` — Add a quarterly region-failover drill for <feature>.
- `infra.gateway-routing-audit` — Audit gateway routing rules for unintended fallbacks to expensive providers.
- `infra.observability-gap-close` — Add the missing trace attribute / span name that hindered diagnosis.

## Commercial — actions

- `commercial.price-table-snapshot` — Snapshot provider price table daily; alert on drift.
- `commercial.rate-limit-monitor` — Add provider rate-limit headroom monitor; alert on shrinkage.
- `commercial.contract-review` — Flag a contract clause that affected response (e.g., provider's right to silently update model).

## Process — actions

- `process.release-gate-add` — Add gate <X> to release pipeline.
- `process.canary-policy-tighten` — Tighten canary criteria; e.g., require 24h canary on prompt changes.
- `process.oncall-handoff-improve` — Add a structured handoff step covering active mitigations and signals.
- `process.runbook-update` — Update per-class playbook to add the move discovered in this incident.
- `process.severity-rule-add` — Add severity-matrix rule reflecting the escalation discovered.

## Comms / Postmortem — actions

- `comms.template-prestage` — Add the failure-class status-page template to the comms tool autoload list.
- `comms.regulator-clock-check` — Add a regulator-clock tracker that pages comms-lead at T+0 of detection.
- `comms.csm-playbook` — Add tenant DM template per severity to CSM playbook.
- `comms.public-summary-template` — Add a public-summary template for this failure class.

## Common Anti-Pattern Action Items (Avoid)

- "Improve monitoring." — Specify which signal at what threshold owned by whom.
- "Add more tests." — Specify which test, in which suite, covering which axis.
- "Train the team." — Specify which session, which audience, which materials.
- "Communicate better." — Specify which template, which channel, which timing.
- "Make the system more robust." — Specify which primitive, which scope, which verification.

## Closing Items

An action item is **closed** only when:
1. The change is shipped (PR merged, config rolled out).
2. Verification check returns the expected observation.
3. The closer is **not** the owner — a second engineer verifies.
4. The closure is logged in `ai_postmortem_actions`.

If verification fails, the item reopens; closure stat is reverted. Do not close on the basis of "I think it's done."
