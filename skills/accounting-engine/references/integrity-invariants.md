# Accounting Integrity Invariants

## Nightly Job

Every tenant gets a scheduled integrity job from day one. Run by period, store the result in `accounting_integrity_runs`, and alert operators on failure.

Required checks:

- `journal_entry_id` debit total equals credit total.
- No journal line exists without a valid active account at posting time.
- No journal line exists outside its tenant.
- No posted journal was changed after posting.
- No locked-period posting exists outside an approved reopening workflow.
- AR, AP, inventory, fixed assets, payroll, tax, bank, and mobile-money control accounts reconcile to tagged journal lines or source registers.
- Trial balance, income statement, balance sheet, and cash flow regenerate from journal lines.
- Materialized balance caches rebuild to stored values.

## Review Gate

Reject a pull request if it:

- Inserts, updates, deletes, or soft-deletes journal lines outside the posting service.
- Adds authoritative balance columns without a rebuild path.
- Hardcodes account codes in business modules.
- Treats an external accounting product as the primary ledger.
- Adds LIFO as an available IFRS costing method.
