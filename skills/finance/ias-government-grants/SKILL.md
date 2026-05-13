---
name: ias-government-grants
description: Government grants and assistance under IAS 20 (full IFRS) and Section 24 (IFRS for SMEs). Recognition, measurement, presentation (gross vs net), conditions, repayable assistance, donor restrictions for NGOs, grant utilisation reporting. Use when government or donor grants are in scope, especially for NGOs, schools, agribusiness, and projects under restricted funding.
---

# Government Grants and Donor Assistance (Section 24 / IAS 20)

## Overview

Section 24 (IFRS for SMEs) provides two methods, electable by entity policy: the **performance model** (recognise income when performance conditions are met or when no conditions exist) and the **accrual model** (deferred income released to P&L as related expenses are incurred or assets are depreciated).

IAS 20 (full IFRS) follows the accrual model and a related-asset / related-income split, with the option of presenting grants related to assets gross (as deferred income) or net (deducted from the asset).

Both standards distinguish:

- Unconditional grants (recognised when receivable).
- Conditional grants (recognised when conditions are met).
- Repayable assistance (treated as liability until repayment terms are met).

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/ifrs-for-smes-default.md` (Section 24)
- `doctrine/references/full-ifrs-overlay.md` (IAS 20)
- `doctrine/references/chart-of-accounts.md`
- `management-accounting-dimensions` SKILL (donor restrictions)

## Donor (NGO) specifics

NGOs typically operate with restricted funds:

- **Unrestricted:** general operating funds; recognise as income when receivable.
- **Restricted (temporary):** purpose- or time-restricted; release to unrestricted when restriction is satisfied.
- **Restricted (permanent):** endowment-like; income earned recognised as restricted unless terms permit reclassification.

The Chwezi NGO model uses dimensions (`grant` / `donor-restriction`) and a fund-balance model alongside the IFRS reporting:

- Donor reporting (utilisation per grant, eligible costs per donor budget).
- IFRS reporting (Section 24 / IAS 20 P&L and balance-sheet effect).

## CoA implications

| Code | Name |
|---|---|
| 4400 Other Operating Income — Government Grants (or Donor Income) | P&L (gross presentation). |
| 2200 Deferred Income — Grants | Liability (accrual model). |
| 2210 Repayable Government Assistance | Liability. |
| Fund-balance accounts | Per restriction (in equity or in a restricted-fund equity section). |

## Build implications

- Grant register: donor, agreement, grant amount, period, conditions, currency, restrictions, eligibility rules.
- Grant draw / receipt workflow.
- Performance / accrual model selection per entity.
- Conditions checklist per grant.
- Eligible-cost categorisation against grant budget.
- Utilisation report per donor per period.
- Restriction-release rules and journals.
- Repayment workflow where conditions are not met.

## Forbidden patterns

- Conditional grant recognised before conditions are met (blocker).
- Donor restrictions ignored in journal flows (blocker).
- Repayable assistance recognised as income (blocker).
- Cross-grant funding (using donor A's funds for donor B's eligible costs) without explicit agreement and disclosure (blocker for NGOs).
- Grant netted against an asset without disclosure of the alternative gross presentation (major where material).

## Files

- `SKILL.md`.
- `references/grant-register-schema.md`.
- `references/donor-restriction-pattern.md`.
- `examples/ngo-restricted-grant-cycle.md`.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
