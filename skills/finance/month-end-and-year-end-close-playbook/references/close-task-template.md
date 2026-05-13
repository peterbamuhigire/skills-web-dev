# Close-Task Template

Template structure for every close task. Stored as YAML in the close-board.

## Schema

```yaml
- id: "close-2026-05-AR-001"
  group: "AR"
  title: "Confirm all AR invoices posted with cut-off"
  description: "Review draft and awaiting-approval invoices dated within the period and ensure they are posted or explicitly deferred."
  owner_role: "Accountant"
  owner_name: "..."
  depends_on: []
  due: "2026-06-02"
  evidence:
    - "AR cut-off review report"
    - "Draft invoice listing as at close"
  state: open | in-progress | blocked | done | exception
  blocker_reason: ""
  signed_by: ""
  signed_at: ""
  reviewed_by: ""
  reviewed_at: ""
  notes: ""
```

## Default task set per area

(See SKILL.md for the area list. Each task below carries the schema above.)

### Pre-close

- `pre-001` Cut-off review for sales.
- `pre-002` Cut-off review for purchases.
- `pre-003` Cut-off review for inventory movements (receipts, issues, transfers).
- `pre-004` GRNI clear: every goods receipt either matched to a supplier invoice or accrued.
- `pre-005` Outstanding manual-journal queue cleared or moved to next period.
- `pre-006` AR ageing review with reminders sent for high-ageing items.
- `pre-007` AP ageing review with priority payments scheduled.

### AR

- `ar-001` All invoices in scope posted.
- `ar-002` All receipts in scope posted.
- `ar-003` Credit notes posted.
- `ar-004` AR control account ties to AR subledger.
- `ar-005` Allowance for doubtful debts reviewed.
- `ar-006` AR ageing report generated.

### AP

- `ap-001` All bills in scope posted.
- `ap-002` All payments in scope posted.
- `ap-003` Credit notes posted.
- `ap-004` AP control account ties to AP subledger.
- `ap-005` AP ageing report generated.
- `ap-006` WHT certificates issued where applicable.

### Inventory

- `inv-001` All receipts posted.
- `inv-002` All issues posted.
- `inv-003` All transfers posted.
- `inv-004` Inventory count variance reviewed.
- `inv-005` Inventory control account ties to inventory subledger.
- `inv-006` NRV write-downs assessed.
- `inv-007` Obsolescence allowance reviewed.
- `inv-008` Inventory valuation report generated.

### Fixed Assets

- `fa-001` Additions posted.
- `fa-002` Disposals posted.
- `fa-003` Depreciation run committed.
- `fa-004` Fixed-asset register reconciled to GL.
- `fa-005` Impairment indicators reviewed.

### Payroll

- `pay-001` Payroll run committed.
- `pay-002` PAYE schedule complete.
- `pay-003` NSSF schedule complete.
- `pay-004` WHT (where applicable) schedule complete.
- `pay-005` Payroll register vs GL reconciled.
- `pay-006` Statutory remittance journals posted.

### Reconciliations

- `rec-bank-<account>` Bank account reconciled, evidence pack attached.
- `rec-momo-<provider>` Mobile-money account reconciled.
- `rec-pos-<location>` POS Z-reports reconciled.
- `rec-card-<acquirer>` Card acquirer settlements reconciled.
- `rec-petty-<imprest>` Petty cash counted.
- `rec-cash-<location>` Cash on Hand counted.

### Tax

- `tax-vat` VAT control account ties to VAT return pack.
- `tax-paye` PAYE control account ties to PAYE return pack.
- `tax-wht` WHT control account ties to WHT return pack.
- `tax-nssf` NSSF control account ties to NSSF return pack.
- `tax-it` Income tax provision computed and posted.
- `tax-source-register` Source-register entries verified-current for the period.

### Adjustments

- `adj-001` Accruals.
- `adj-002` Prepayments.
- `adj-003` Depreciation.
- `adj-004` FX revaluation.
- `adj-005` Provisions review.
- `adj-006` Allowance for doubtful debts.
- `adj-007` NRV write-downs.

### Reports

- `rep-tb` Trial balance.
- `rep-sfp` SFP.
- `rep-soci` SOCI.
- `rep-sce` SCE.
- `rep-scf` SCF.
- `rep-ar-age` AR ageing.
- `rep-ap-age` AP ageing.
- `rep-inv-val` Inventory valuation.
- `rep-fa` Fixed-asset register.
- `rep-payroll` Payroll register vs GL.
- `rep-mgmt` Management accounts pack with variance commentary.
- `rep-donor` Donor / grant utilisation (where applicable).
- `rep-audit-export` Audit-ready export index.

### Release

- `rel-001` Reviewer sign-off (Controller).
- `rel-002` Period soft-close.
- `rel-003` Gate manifest produced.
- `rel-004` Lock period (after waiting window).

## Dependencies (illustrative)

```
pre-001 → ar-001
pre-002 → ap-001
pre-003 → inv-001, inv-002, inv-003
inv-001..003 → inv-004 → inv-005 → inv-008
fa-001..002 → fa-003 → fa-004
pay-001 → pay-005 → adj-* (where payroll impacts accruals)
ar-001..003 → ar-004 → ar-006
ap-001..003 → ap-004 → ap-005
{rec-*} → tax-*
{adj-*} → rep-tb → rep-sfp / rep-soci / rep-sce / rep-scf
{rep-*} → rel-001 → rel-002 → rel-003 → rel-004
```

## Evidence locations

Every task evidence path resolves to the entity evidence root:

```
evidence/<entity>/<period>/<area>/<task-id>/
```

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
