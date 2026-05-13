---
name: finance-ui-pattern-library
description: Production UI patterns, design tokens, role-conditioned shells, drilldown primitives, reconciliation triage layout, print stylesheet patterns, status taxonomy components, and money-cell components for Chwezi finance and accounting products. Use when designing or building any finance / accounting screen, dashboard, report, print layout, mobile cashier flow, accountant ledger surface, reconciliation UI, close board, return-pack viewer, or audit-ready export across any consumer engine. Auto-load when the user requests UI / UX work that touches money, inventory, payroll, tax, banking, mobile money, POS, statutory compliance, or accounting records.
---

# Finance UI Pattern Library

## Overview

This skill is the production reference for finance and accounting UI in the Chwezi system. It enforces the doctrine in `doctrine/references/design-system-finance-accounting.md`, `design-anti-patterns.md`, `role-conditioned-shell.md`, `status-taxonomy.md`, and `print-fidelity.md`. It provides design tokens, component contracts, lint rules, and worked examples.

## Required first reads

Before generating any finance UI:

1. `doctrine/accounting-finance-doctrine.md`
2. `doctrine/references/design-system-finance-accounting.md`
3. `doctrine/references/design-anti-patterns.md`
4. `doctrine/references/role-conditioned-shell.md`
5. `doctrine/references/status-taxonomy.md`
6. `doctrine/references/print-fidelity.md`
7. This skill's `references/tokens.md` and `references/components.md`.

## Scope

This skill applies to:

- Any HTML / CSS / React / Vue / Svelte / mobile-native finance UI.
- Print stylesheets.
- Email and notification finance-content templates.
- PDF report renderers.
- Dashboard tiles.
- Documentation / marketing pages that show product screenshots.

## Workflow

1. Identify the surface mode (workflow / ledger / auditor read-only / configuration).
2. Confirm the role(s) that will use the screen.
3. Pull the relevant component contracts from `references/components.md`.
4. Apply the tokens from `references/tokens.md`.
5. Add the role-conditioned shell wrapper.
6. Include the drilldown affordance on every money figure.
7. Apply the status taxonomy.
8. Add the print stylesheet for any report or evidence pack.
9. Run the lint script in `references/lint-checks.md` before merging.
10. Record a screenshot in the PR.

## Components shipped

The `references/components.md` file documents:

- `MoneyCell` — tabular numerals, currency code, sign colouring (signed columns only), drilldown.
- `NetTaxGrossTriplet` — three adjacent cells; never collapsed.
- `StatusChip` — uses controlled taxonomy; works in monochrome print.
- `PeriodChip` — top-bar period state chip.
- `EntityBookSwitcher` — multi-entity / multi-book switcher.
- `RoleSwitcher` — when the user has multiple roles.
- `EnvironmentBanner` — non-prod environment banner.
- `DrilldownBreadcrumb` — Report → Account → Journal → Line → Source → Evidence.
- `PostingForm` — net / tax / gross fields, evidence dropzone, audit-log preview.
- `ReconciliationTriage` — two-pane layout with centre actions and ageing.
- `LedgerGrid` — dense grid; keyboard-first; sticky headers and totals.
- `CloseBoard` — close tasks with owner, due, evidence, status.
- `ReturnPackViewer` — period selector, line mapping, source documents, evidence.
- `AuditExport` — read-only ledger with watermark.
- `PrintHeader`, `PrintFooter`, `SignOffBoxes`.
- `EvidenceDropzone` — inline on posting forms.

## Lint rules (excerpt)

The lint script in `references/lint-checks.md` rejects:

- `<button>` with destructive verb on a posted record.
- `text-green` / `text-red` / `bg-green` / `bg-red` outside semantic-state contexts.
- Money rendering without `font-variant-numeric: tabular-nums`.
- A summary tile without an `onClick` / `Link` affordance to source.
- A status string not matching the controlled taxonomy.
- A report page without `@media print` styles.

## What forbidden patterns are caught

This skill enforces 32 patterns from `design-anti-patterns.md` automatically; the remaining 26 require human review.

## Auto-loading

This skill is referenced from each engine's `CLAUDE.md` "Finance & Accounting Trigger" block. When the request is UI-flavoured (HTML, CSS, JSX, mobile native code, screen mock, dashboard, report, print) and finance scope is detected, this skill is loaded automatically alongside the doctrine.

## Files

- `SKILL.md` — this file.
- `references/tokens.md` — token JSON and CSS variables.
- `references/components.md` — full component contracts.
- `references/lint-checks.md` — checklist and grep / AST patterns.
- `references/print-stylesheet-template.md` — copy-paste `@media print` template.
- `examples/cashier-record-sale.md` — full mock of a workflow-surface screen.
- `examples/ledger-trial-balance.md` — full mock of a ledger-surface screen.
- `examples/reconciliation-triage.md` — full mock of the reconciliation UI.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
