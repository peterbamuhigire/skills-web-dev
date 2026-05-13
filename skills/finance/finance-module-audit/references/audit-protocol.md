# Audit Protocol

The procedure used by the `finance-module-audit` skill against any target system. Aligned to doctrine v1.0.0.

## Phase 1 — Scoping (always)

Collect:

| Field | Notes |
|---|---|
| System name | |
| Owner / vendor | |
| Repositories | All; not just one |
| Data stores | RDBMS, document, queue, cache, blob |
| Integrations | Banks, mobile money, EFRIS, eTIMS, card acquirers, payroll providers |
| Jurisdiction | Country and any sub-jurisdiction |
| Reporting framework | IFRS / IFRS for SMEs / local statutory / client-specific / N/A |
| Sectors | Retail, school, clinic, NGO, manufacturing, agribusiness, hospitality |
| User roles | Cashier, clerk, manager, accountant, controller, auditor, admin |
| Deployment | On-prem, cloud, hybrid |
| Audience | Operational, statutory, donor, audit |

Outcome: scope record stored with the audit.

## Phase 2 — Artefact inventory

Pull every artefact: source code, schema, migrations, seed data, tests, SRS / SDS, proposal, business-plan finance section, screenshots, reports, exports, deployment settings, dashboards, prints. Where access is gated, list the gap.

## Phase 3 — Money-flow map

Map for each in-scope flow: trigger event → role → workflow surface → posting service → CoA accounts → subledger → reconciliation → close → reporting → tax pack. For each, identify:

- Whether VAT-inclusive decomposition is enforced.
- Whether EFRIS / eTIMS submission is part of the flow.
- Whether the reversal path is exercised.
- Whether the audit log captures the actor, evidence, lineage.

## Phase 4 — Accounting-integrity tests

For each invariant in `doctrine/references/ledger-invariants.md`:

| Invariant | How to test |
|---|---|
| Posting boundary | Grep / static analysis for direct writes to journal tables outside the posting service. |
| Double entry | Sample 50 posted journals: every one balances per currency. |
| Immutability | Attempt to edit / delete a posted journal via every UI affordance and every API endpoint. |
| Reversal | Reverse a posted journal; verify lineage, reason, actor, reversal type. |
| Period state | Attempt to post into `locked`; should reject. |
| Audit log | Pull last 100 ledger postings; every one has actor, time, evidence, lineage. |
| Idempotency | Replay a posting command with same key, then same key + different payload; verify reject. |
| Control-account tie-out | Sample 5 close periods: control = subledger sum to the unit. |

## Phase 5 — UX tests

Role by role, run the standard workflows from `doctrine/references/role-conditioned-shell.md`. Verify:

- Workflow vs ledger surface present.
- Period chip visible.
- Drilldown affordance on every money figure.
- Status taxonomy use.
- Net / tax / gross triplet on VAT-inclusive screens.
- No `Delete` on posted records.
- Print fidelity.
- Reconciliation triage as a triage UI, not a report.
- Low-bandwidth tolerance: offline drawer close, optimistic post + reconcile.

## Phase 6 — Compliance tests

- Framework header on every finance artefact.
- US GAAP only as explicit overlay.
- LIFO blocked under IFRS / IFRS for SMEs.
- VAT-inclusive decomposition.
- Return-ready packs produced for each authority in scope.
- Live-rate verification: every rate / threshold / template has a source-register entry in `verified-current` state (or `pass-with-caveats` with named owner).
- Country-extension structure honoured for non-Uganda jurisdictions.

## Phase 7 — Operational tests

- Reconciliation: bank, mobile money, POS, card, cash. Each with evidence pack.
- Close: tasks, owners, dependencies, evidence, release state.
- Audit-ready pack: minimum content per `audit-ready-reporting-pack` skill.
- Internal controls: SoD, maker-checker, master-data, audit-log review, exception monitoring.
- Migration: cutover pack complete; suspense zero or waived.
- Management dimensions: governed; reconcile to GL.

## Phase 8 — Scoring and release decision

Apply `scorecard.md`. Classify blockers vs caveats vs passes. Produce the release decision: `pass`, `pass-with-caveats`, `fail`.

## Phase 9 — Master plan

Build the remediation master plan per `remediation-master-plan.md` — phased, with owners, acceptance evidence, and dependencies.

## Evidence handling

- Inspect source artefacts; do not certify from screenshots alone.
- Treat all rates / thresholds / statutory defaults / exchange rates as live facts requiring current-source verification.
- Mark every unsupported assertion as a gap or inference.
- Never claim 100 % compliance unless every required control is evidenced, tested, and current-source verified.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
