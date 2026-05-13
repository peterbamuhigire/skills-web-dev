---
name: management-accounting-dimensions
description: Governed dimensions (cost centre, project, grant, donor restriction, department, branch, product line, customer, supplier, activity, currency, book) and the budget / variance / allocation / contribution-margin / donor-grant reporting they support. Use when designing or implementing management reporting, KPI dashboards, budget vs actual, project profitability, grant utilisation, contribution-margin analysis, or allocation rules. Applies in software, SRS, SDS, test plan, proposal, and business-plan contexts.
---

# Management Accounting Dimensions

## Overview

Management accounting is built on governed dimensions tied to the ledger. Informal tags do not reconcile and do not survive close. Every dimension is defined in the entity configuration, has a permissions model, and is required / permitted at the CoA-account level.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/chart-of-accounts.md` (Dimensions section)
- `doctrine/references/required-patterns.md`
- This skill's `references/dimensions-spec.md`.

## Standard dimensions

| Dimension | Use |
|---|---|
| Entity | Legal entity context in multi-entity books. |
| Branch / site / location | Operating location. |
| Department | Org-chart unit. |
| Cost centre | Cost-aggregation unit independent of department. |
| Project / job | Time-bounded effort with budget. |
| Grant / fund | Restricted funding source. |
| Donor restriction | Use restriction tied to a grant. |
| Product line / SKU / category | Revenue and cost-of-sales decomposition. |
| Customer / supplier | Where revenue or expense ties to a specific counterparty for management view. |
| Activity / channel | Sales channel, programme activity. |
| Currency / book | Transactional currency and reporting book. |

## Required at CoA level

The CoA records per account:

- Dimensions **required** (must be present on every posting).
- Dimensions **permitted** (optional but allowed).
- Dimensions **forbidden** (must not appear).

The posting service rejects postings that violate the matrix.

## Capabilities

### Budgets

- Budget versions per entity per period per book.
- Budget granularity per dimension.
- Approval workflow: draft → approved → final → locked.
- Final-version lockdown: only Controller + CFO can unlock; audit-logged.

### Budget vs Actual

- By any combination of dimensions.
- Variance commentary required where variance exceeds threshold.
- Drilldown into the variance: report → account → journal → line → source.

### Standard costing and variance analysis

Where stock or manufacturing is in scope:

- Standard cost set per SKU per period.
- Material price variance, material usage variance, labour rate variance, labour efficiency variance, overhead absorption variance.
- Variances flow to standard-cost variance accounts in the CoA.

### Allocation rules

- Source pool (the cost / revenue to allocate).
- Basis (headcount, square meterage, sales, activity-based driver, …).
- Recipient dimensions (which cost centres / projects receive the allocation).
- Approval: Controller.
- Audit trail: every allocation journal links to the allocation rule and the basis driver value at the period.

### Contribution-margin reporting

Per product line, branch, channel, customer segment, or project:

- Revenue
- Variable costs (cost of sales, variable selling costs)
- Contribution margin
- Allocated fixed costs (clearly marked as allocated)
- Operating profit before central overhead
- Central overhead allocation (optional)

### Donor / grant reporting

- Restrictions tied to the grant master record.
- Eligible costs categorised per donor budget.
- Utilisation report per grant per period: budget vs actual eligible costs vs total spend.
- Variance approval per donor rules.
- Audit trail per donor reporting requirement.

## Forbidden patterns

- Free-text tags as dimensions (blocker).
- Postings to dimension-required accounts without dimensions (blocker).
- Allocation rules that don't store the basis driver value at the time of allocation (major).
- Management reports that don't reconcile to the GL (blocker).
- Variance commentary missing where threshold is exceeded (major).
- Donor reports without restriction enforcement (blocker).

## Acceptance evidence

- Dimension registry (configuration).
- Posting-service tests: each account's required / permitted / forbidden matrix enforced.
- Budget version lifecycle tested.
- Allocation rule audit-log entries.
- Management pack reconciliation to GL.
- Donor pack with restriction enforcement evidence.

## Files

- `SKILL.md`.
- `references/dimensions-spec.md` — full dimension specification.
- `references/allocation-rules-pattern.md` — allocation rule shapes.
- `examples/contribution-margin-by-branch.md` — worked example.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
