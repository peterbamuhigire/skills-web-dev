---
name: fixed-assets-and-depreciation
description: >-
  Use when designing or reviewing fixed asset accounting under IAS 16/IFRS for SMEs:
  asset register, capitalization, directly attributable costs, depreciation, disposals,
  revaluation policy, custody, and asset-register-to-GL reconciliation.
metadata:
  portable: true
---

# Fixed Assets And Depreciation
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

## Use When

- The system buys, capitalizes, depreciates, revalues, transfers, impairs, or disposes of fixed assets.
- Asset reports must reconcile to the GL.

## Hard Rules

- MUST maintain an asset register separate from, but reconciled to, the GL.
- MUST post depreciation through the single ledger posting service.
- MUST separate cost, accumulated depreciation, carrying amount, disposal proceeds, and gain/loss.
- MUST expense routine repairs and capitalize only qualifying improvements or directly attributable acquisition costs.

## Asset Register Fields

Minimum fields: tenant, asset number, category, description, acquisition date, available-for-use date, cost, residual value, useful life, depreciation method, location, custodian, funding source where relevant, disposal date, disposal proceeds, status.

## Depreciation Methods

- Straight-line.
- Reducing balance.
- Units of production.

Monthly depreciation:

- Debit depreciation expense.
- Credit accumulated depreciation.

Disposal:

- Debit cash/receivable for proceeds.
- Debit accumulated depreciation.
- Credit asset cost.
- Debit loss or credit gain on disposal for the balancing amount.

## Revaluation

Use only when tenant accounting policy permits it and valuation evidence exists. Revaluation surplus, reversals, depreciation impact, and disclosures require accountant review.

## Outputs

- Asset register design.
- Depreciation policy.
- Posting matrix.
- Disposal workflow.
- Asset-register-to-GL reconciliation.
