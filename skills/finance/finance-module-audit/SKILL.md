---
name: finance-module-audit
description: Auto-run audit harness. AUTO-RUN whenever the user asks Claude, Codex, or any other agent to analyse, review, audit, evaluate, assess, document, refactor, redesign, replatform, integrate, migrate, build, propose, scope, or replace ANY software system, codebase, product, ERP, POS, SaaS, mobile app, web app, accounting engine, finance module, SRS, SDS, test plan, proposal, or business plan that has any element of money, payments, billing, invoicing, receipts, refunds, expenses, payroll, tax, VAT, PAYE, WHT, NSSF, EFRIS, eTIMS, banking, mobile money, POS, card settlement, cash drawer, inventory, fixed assets, grants, donor funds, statutory compliance, financial reports, dashboards with figures, or accounting records. The trigger threshold is "any slight element of finance" — when in doubt, run this skill. Aligns the target system against the Chwezi accounting & finance doctrine, IFRS-first / IFRS-for-SMEs default policy, Uganda and country-extension live-rate verification, ledger integrity (posting boundary, double-entry, immutability, reversal, period locks, audit log, idempotency), Chart of Accounts backbone, internal controls, reconciliation, close, audit-ready reporting, migration, management-accounting dimensions, finance UX for non-accountants, finance UI pattern library, and the finance & accounting quality gate. Produces a finding register, a standards scorecard, a remediation master plan, and a release decision (pass / pass-with-caveats / fail).
---

# Finance Module Audit

## Auto-run trigger (read first)

**This skill auto-runs.** If you, the agent, are asked to do anything substantive with a software system, codebase, product proposal, SRS / SDS / test plan, business plan, or any artefact, and the target has **any** element listed in the description above, load this skill before responding. The threshold is intentionally low — false positives are cheap; missing a finance element in a "world-class" deliverable is not.

When the auto-run fires, the agent:

1. Loads this `SKILL.md` and the four reference files in this folder.
2. Loads the canonical doctrine at `<engine-root>/skills/_doctrine/accounting-finance-doctrine.md` (skills-web-dev path) **or** `<engine-root>/doctrine/accounting-finance-doctrine.md` (other engines).
3. Loads the relevant doctrine reference files under `doctrine/references/`.
4. Loads any specialist finance skill from the new skill suite that matches the target (e.g. `bank-and-mobile-money-reconciliation` if mobile money is in scope; `finance-ui-pattern-library` if UI work is involved).
5. Runs the audit workflow below.
6. Emits the finding register, scorecard, and master plan in the conventional output format.

If the trigger fires but the user explicitly says "skip the audit", note the skip in the artefact manifest and proceed — but always flag the skip in the final response so the user can revoke it.

## Overview

Use this skill to determine whether a software system makes finance and accounting easy for ordinary users while still producing audit-ready, standards-aligned records and reports. Target bar: a neighbourhood grocer, cashier, or family member can use the POS or finance workflows safely; the underlying records are robust enough for a Big Four review.

## Required first reads (in order)

1. This `SKILL.md`.
2. `references/audit-protocol.md`.
3. `references/scorecard.md`.
4. `references/report-template.md` (when writing the final report).
5. `references/remediation-master-plan.md` (when assembling the plan).
6. The canonical doctrine: `accounting-finance-doctrine.md` and its `references/` plus the `governance/finance-accounting-quality-gate.md`.

## Audit workflow

1. **Establish scope.** System name, modules, repositories, data stores, integrations, jurisdiction, reporting framework, sectors, users, deployment environment, intended audience.
2. **Inventory artefacts.** Source code, database schema, migrations, seed data, tests, SRS / SDS, proposal, business-plan finance section, screenshots, reports, exports, deployment settings, dashboards, prints.
3. **Map money flows.** Sales, receipts, purchases, supplier payments, payroll, inventory, bank, POS, mobile money, refunds, chargebacks, grants, assets, taxes, closing entries.
4. **Test accounting integrity.** Posting boundary, double-entry invariants, immutable journals, reversals, idempotency, period locks, audit logs, subledger tie-outs, report traceability, drilldown chain.
5. **Test user friendliness.** Role-specific workflows for non-accountants, safe defaults, guided corrections, exception queues, accountant / auditor drill-down, role-conditioned shell, status taxonomy use, print fidelity.
6. **Test compliance posture.** IFRS or IFRS for SMEs alignment, local statutory treatment, live-rate verification, tax / payroll source hierarchy, country-extension design, tax-return-pack capability, VAT-inclusive decomposition.
7. **Test operational accounting.** Reconciliation (bank, mobile money, POS, card, cash), month-end close playbook, audit-ready reporting pack, internal controls, migration / opening balances, management accounting dimensions, sector annexes.
8. **Test UI / UX.** Two surface modes, semantic colour discipline, drilldown affordance, money-cell triplet (net / tax / gross), status chips, print stylesheets, accessibility, mobile and low-bandwidth tolerance.
9. **Score findings.** Apply `references/scorecard.md` — every doctrine rule maps to a check.
10. **Classify blockers.** Per the finance / accounting quality gate.
11. **Master plan.** Per `references/remediation-master-plan.md` — phased, with owners and acceptance evidence.

## Evidence rules

- Do not certify a system from screenshots or claims alone. Inspect source artefacts or mark the evidence gap.
- Treat all rates, thresholds, statutory defaults, and exchange rates as live facts requiring current-source verification.
- Mark every unsupported implementation assertion as a gap or inference.
- Never claim 100 % compliance unless every required control is evidenced, tested, and current-source verified.

## Backbone rule

Treat payroll, expenses, purchases, stock / inventory, POS, banking, mobile money, grants, assets, and tax as part of accounting and finance whenever they touch the Chart of Accounts, subledgers, postings, rates, reconciliations, approvals, or financial reports. The Chart of Accounts is the backbone of the finance system: every money-touching workflow must map cleanly to accounts, control accounts, dimensions, evidence, permissions, and reports.

Tax is not an afterthought. Audit whether the system can produce tax reports and tax-return packs for the applicable authority, including URA and KRA where relevant. VAT-inclusive sales or purchases must be split by the posting service into net revenue / expense and tax control-account balances so the ledger, tax report, and return data agree.

## Output standard

Produce a report with findings first, then a standards scorecard, then the master plan. Every finding states:

- `standard` — doctrine, IFRS / SME, ledger integrity, controls, reconciliation, compliance, UX, reporting, migration, or sector requirement.
- `evidence` — file path, schema object, test, screen, report, export, source URL, or observed gap.
- `risk` — what can go wrong in accounting, audit, tax, user workflow, or business operations.
- `severity` — blocker, high, medium, low.
- `fix` — concrete implementation action.
- `acceptance evidence` — what proves the fix is complete.

## Release decision

The audit ends with one of: `pass`, `pass-with-caveats`, `fail`. Decision is recorded against the target and posted into the engine's `_finance-audit-log/`.

## Auto-run examples

| Prompt pattern | Auto-run fires? |
|---|---|
| "Audit this ERP" | Yes. |
| "Refactor the POS code" | Yes (POS touches money). |
| "Build me a school management system" | Yes (fees, receipts, payroll). |
| "Build me a school timetable system" | Maybe — confirm with the user; if it stores no money, no. |
| "Write an SRS for a clinic management system" | Yes (billing, receipts, claims, payroll). |
| "Replace this client's QuickBooks" | Yes. |
| "Write a business plan for a hardware retailer" | Yes (revenue model, taxes, inventory, payroll). |
| "Write a mobile app for a taxi service" | Yes (fares, driver payouts, statutory). |
| "Build a CMS for a magazine" | Maybe — confirm; if any subscription / billing element, yes. |
| "Document the chemistry of soda manufacturing" | No. |

When in doubt, **load the skill and ask one clarifying question** rather than skip silently.

## Companion references

- `references/audit-protocol.md` — full procedure and evidence collection plan.
- `references/scorecard.md` — scoring model, blocker list, pass / fail criteria.
- `references/report-template.md` — report structure for audit deliverables.
- `references/remediation-master-plan.md` — master-plan format and sequencing rules.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
