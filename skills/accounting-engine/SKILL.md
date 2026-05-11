---
name: accounting-engine
description: Use when designing, implementing, or reviewing an embedded accounting engine inside a SaaS, ERP, POS, inventory, payroll, school, clinic, NGO, marketplace, or mobile-money-heavy system. Covers one append-only general ledger, one LedgerPostingService write path, mapping-layer account resolution, IFRS/IFRS for SMEs defaults, subledger tagging, idempotent posting, reversing journals, period locks, audit trails, report projections, and accounting integrity tests.
metadata:
  portable: true
  default_standard: IFRS for SMEs
---

# Accounting Engine

## Use When

- The product handles money, inventory value, payroll, tax, customer balances, supplier balances, assets, grants, donations, loans, refunds, wallet balances, or financial reporting.
- A SaaS must replace routine bookkeeping in external products such as QuickBooks, Xero, Sage, Pastel, Tally, Zoho Books, or Wave.
- You need architecture, schema, posting rules, tests, documentation, or review findings for ledger-backed business software.

## Do Not Use When

- The task is only financial analysis or projections without software architecture; use `accounting-finance-controller` or the business-plan finance skills.
- The system only displays imported accounting reports and does not create business events or postings.
- A jurisdiction requires a licensed accountant, auditor, or tax practitioner to exercise professional judgement; design the system support, but do not claim the software replaces that judgement.

## Hard Rules

- NEVER let a business module write directly to `gl_entries`, `journal_lines`, `journal_entries`, or any ledger table.
- ALWAYS write ledger records through one service: `LedgerPostingService::post(JournalEntry $entry)` or the project-equivalent single posting service.
- NEVER update, delete, or soft-delete posted journal lines. Corrections are reversing journals linked to the original entry.
- NEVER store authoritative balances that cannot be rebuilt from journal lines. Materialized balances are caches with a documented rebuild command.
- NEVER hardcode account codes in business logic. Use account mappings resolved at posting time.
- NEVER use LIFO for IFRS or IFRS for SMEs tenants.
- MUST reject posting when required account mappings are missing, inactive, cross-tenant, or not valid for the source document.

## Canonical Architecture

Business modules emit events. A mapper turns events into balanced `JournalEntry` value objects. The posting service validates and writes the entry atomically. Reports, subledgers, balances, tax schedules, and dashboards are deterministic projections of the ledger.

```text
Sales / Stock / Payroll / Assets / Payments / Grants
        -> business event
        -> account resolver and posting-rule mapper
        -> JournalEntry value object
        -> LedgerPostingService::post()
        -> append-only journal_entries + journal_lines
        -> reports, subledgers, tax schedules, dashboards
```

## Required Model

Core tables:

- `chart_of_accounts`
- `account_mappings`
- `journal_entries`
- `journal_lines`
- `accounting_periods`
- `posting_rule_versions`
- `accounting_integrity_runs`
- `accounting_audit_log`

Every accounting table MUST carry `tenant_id`, unless the product is explicitly single-tenant. If legacy files use `franchise_id`, treat it as a project-specific tenant alias and document the mapping.

## Posting Service Contract

```php
<?php
declare(strict_types=1);

final readonly class JournalEntry
{
    public function __construct(
        public int $tenantId,
        public string $idempotencyKey,
        public DateTimeImmutable $entryDate,
        public string $sourceType,
        public string $sourceId,
        public string $description,
        /** @var list<JournalLine> */
        public array $lines,
        public ?int $reversesJournalId = null,
    ) {}
}

final readonly class JournalLine
{
    public function __construct(
        public int $accountId,
        public string $currency,
        public string $debitMinor,
        public string $creditMinor,
        public array $dimensions = [],
    ) {}
}

interface LedgerPostingService
{
    public function post(JournalEntry $entry): PostedJournal;
}
```

The service validates tenant scope, account status, open period, debit-credit equality, currency policy, idempotency, source document state, and mapping completeness before insert.

## Integrity Checks

Run these per tenant and per accounting period from day one:

- Debits equal credits per `journal_entry_id`.
- Trial balance total debits equal total credits.
- AR control account equals customer-tagged journal line balance.
- AP control account equals supplier-tagged journal line balance.
- Inventory control account equals stock-on-hand value by item/location/cost layer.
- Fixed asset control account equals asset-register cost less disposals.
- Payroll liability accounts equal unpaid statutory and employee deductions.
- No journal exists in a locked period unless it is a permitted reopening workflow with approval evidence.
- No ledger table has rows written outside the posting service.
- Materialized balances rebuild to the same values as stored cache rows.

## User Experience Principle

Non-accountants record business actions: `Record Sale`, `Receive Payment`, `Buy Stock`, `Run Payroll`, `Record Asset Purchase`, `Receive Grant`, `Close Month`. The system posts accounting behind the scenes. Accountant-facing roles get journals, CoA, mappings, period close, manual journal, and report exports.

## Companion Skills

- `chart-of-accounts-templates` for IFRS-aligned industry templates.
- `inventory-costing` for IAS 2 stock valuation and COGS flows.
- `payroll-postings-uganda` for PAYE/NSSF/LST payroll journal shapes.
- `fixed-assets-and-depreciation` for IAS 16 asset lifecycle.
- `multicurrency-and-fx` for IAS 21 currency handling.
- `multi-tenant-saas-architecture`, `api-design-first`, and `advanced-testing-strategy` for platform integration.

## References

- `references/posting-engine-contract.md`
- `references/integrity-invariants.md`
