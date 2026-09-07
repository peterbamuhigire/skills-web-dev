---
name: accounting-finance-controller
description: Use when coordinating accounting and finance implementation reviews, doctrine routing, control evidence, remediation priorities, and release decisions across a software system.
metadata:
  portable: true
  do_not_use_when: Do not use for accounting doctrine alone or for a narrow posting implementation owned by accounting-engine.
  required_inputs: Provide system scope, finance risks, doctrine sources, implementation evidence, and release decision.
  quality_standards: Require traceable doctrine, balanced postings, controls, reconciliation, auditability, and explicit gaps.
  anti_patterns: Do not approve from prose claims, mix doctrine with unverified implementation, or hide unresolved control failures.
  outputs: Produce the controller assessment, routed workstreams, evidence gaps, remediation priorities, and release verdict.
  compatible_with:
  - claude-code
  - codex
---

# Accounting Finance Controller

<!-- dual-compat-start --><!-- dual-compat-end -->

## Inputs

| Artefact | Required? | Purpose |
|---|---|---|
| System scope and finance risk register | yes | Select doctrine and controls |
| Implementation and reconciliation evidence | yes | Determine actual readiness |
| Release decision and owners | yes | Assign remediation and approval |

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Controller assessment and routed work plan | Engineering and finance owners | Evidence-backed findings, owners, priorities, verdict |

## Capability contract

Default to read-only coordination. Ledger mutation, migration, close, filing, or production correction requires separately authorised execution through the owning skill and finance approver.

## Degraded mode

Fallback without doctrine or implementation evidence: issue `Needs Evidence`; do not approve the system or fabricate compliance.

## Decision rules

| Finding | Route | Release effect |
|---|---|---|
| Doctrine uncertainty | External accounting doctrine | Hold affected decision |
| Posting or reconciliation defect | `accounting-engine` | Block affected financial flow |
| Evidence complete and controls effective | Controller approval | Proceed with recorded residual risks |

## Domain anti-patterns

- Approving from design prose alone. Fix: require implementation and reconciliation evidence.
- Mixing policy ownership with code ownership. Fix: route doctrine and implementation separately.
- Treating an unreconciled balance as immaterial by default. Fix: quantify and approve thresholds.
- Hiding unresolved findings in a narrative. Fix: record owner, severity, due date, and release effect.
- Performing production corrections during review. Fix: use a separately authorised remediation workflow.

## Use When

- Designing or implementing financial modules for POS, ERP, SaaS, school fees, healthcare billing, inventory, payroll, project accounting, fixed assets, procurement, or mobile-money-heavy systems.
- Reviewing business plans, proposals, dashboards, spreadsheets, or systems where accounting accuracy, financial controls, investor confidence, or management reporting matter.
- The user wants outputs that feel credible to CFOs, accountants, auditors, lenders, investors, or senior executives.

## Core Rule

Every money movement must have a business event, source document, accounting treatment, posting rule, control, reconciliation path, and report destination. If any link is missing, the system is not finance-ready.

## Workflow

1. Identify the entity type, industry, reporting basis, currency, tax context, transaction volumes, user roles, and whether IFRS/statutory reporting is required.
2. Map business events to ledgers: sales, receipts, purchases, payments, inventory, payroll, tax, fixed assets, loans, owner equity, journals, adjustments, accruals, prepayments, and reversals.
3. Define the chart of accounts, accounting dimensions, control accounts, subledgers, fiscal periods, document numbers, posting rules, and period-close workflow.
4. Build management accounting: cost objects, cost drivers, cost centers, profit centers, contribution margin, CVP, budgets, flexible budgets, variance analysis, and responsibility-center reporting.
5. Add controls: segregation of duties, maker-checker approvals, immutable audit logs, period locks, role permissions, exception queues, reconciliation evidence, and reversal-only correction.
6. Design reports: trial balance, general ledger, P&L, balance sheet, cash flow, aging, inventory valuation, tax schedules, management accounts, dashboards, and board packs.
7. Validate with accounting gates: balanced journals, subledger-to-GL reconciliation, tax timing, inventory costing, cash/bank proof, period close, and model checks.

## Accounting Coverage

- Financial accounting: double-entry, accruals, revenue, expenses, assets, liabilities, equity, financial statements, disclosures, consolidation where relevant.
- Cost accounting: direct/indirect costs, fixed/variable costs, cost drivers, job/process/hybrid costing, ABC, standard costing, CVP, margin of safety, transfer pricing.
- Management control: budgets, responsibility centers, KPIs, performance measurement, incentives, project controls, decentralization, and management reporting cadence.
- IFRS-aware design: accounting policies, estimates, errors, events after reporting date, inventories, PPE, leases, impairment, provisions, financial instruments, cash flow, fair value, and disclosure readiness.
- Advanced accounting: business combinations, goodwill, non-controlling interests, intercompany eliminations, equity method, foreign currency, and group reporting where relevant.
- Quantitative finance: NPV, IRR, payback, effective interest rates, discounting, sensitivity analysis, scenario modelling, risk-return logic, and data-driven forecast checks.

## Quality Gates

- No posted transaction can be edited or deleted; corrections use reversals and adjustment entries.
- Debits equal credits at transaction, batch, period, tenant, and consolidated levels.
- Subledgers reconcile to GL control accounts: AR, AP, inventory, fixed assets, payroll, tax, loans, and bank/mobile money.
- Reports must be reproducible from source transactions, not manually typed summaries.
- Financial projections must connect to operational drivers, not arbitrary growth percentages.
- Budgets compare actuals to flexible budgets, not only static targets.
- Investor or lender numbers must reconcile across narrative, tables, cash flow, balance sheet, funding request, and appendices.

## References

- `references/professional-accounting-systems-gate.md` - detailed checklists for system requirements, IFRS-aware reporting, management accounting, projections, controls, and review.
- Companion skill: `saas-accounting-system` for double-entry implementation patterns and schema-level design.
