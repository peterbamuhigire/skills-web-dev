---
name: chart-of-accounts-templates
description: Use when creating IFRS-aligned chart of accounts templates and default account mappings for SaaS tenants in restaurant/hospitality, retail, professional services, manufacturing, schools, clinics/hospitals, NGOs/fund accounting, and agribusiness. Covers account hierarchy, control accounts, payment methods, tax accounts, revenue categories, COGS, inventory, payroll, fixed assets, grants, and tenant onboarding.
metadata:
  portable: true
---

# Chart Of Accounts Templates

## Use When

- Onboarding a tenant into an embedded accounting engine.
- Creating industry CoA templates, account mappings, or report rollups.
- Reviewing whether business code depends on account codes.

## Do Not Use When

- The task needs only a statutory financial statement format with no software mapping.
- The tenant must use a regulator-prescribed chart; in that case map the prescribed chart into this structure.

## Hard Rules

- NEVER hardcode account codes in business logic.
- MUST clone templates per tenant before customization.
- MUST mark AR, AP, inventory, fixed assets, payroll liabilities, tax, bank, cash, and mobile-money accounts as control accounts where applicable.
- MUST default to IFRS for SMEs unless tenant configuration says full IFRS or another local GAAP.

## Base Account Classes

Use five top-level classes:

- Assets
- Liabilities
- Equity or Net Assets
- Revenue
- Expenses

Recommended subtypes: current asset, non-current asset, current liability, non-current liability, equity/net assets, operating revenue, other income, cost of sales, payroll expense, operating expense, depreciation, finance cost, tax expense.

## Industry Templates

Use `references/industry-coa-templates.md` for starting templates. Each template must include:

- Common revenue categories.
- COGS or cost-of-service categories.
- Inventory, WIP, or supplies accounts where relevant.
- Payment methods: cash, bank, MTN MoMo, Airtel Money, card, petty cash.
- Uganda VAT accounts: output VAT, input VAT, VAT control, zero-rated/exempt configuration. Verify current tax rules before delivery.
- Payroll mappings for gross pay, PAYE, NSSF employee, NSSF employer, LST, advances, loans, net pay.
- Fixed asset categories and accumulated depreciation contra accounts.

## Good / Bad

Bad:

```php
const REVENUE_ACCOUNT = '4100';
```

Good:

```php
$account = $accountResolver->revenueForProductCategory($tenantId, $productCategoryId);
```

## Outputs

- Tenant CoA template.
- Mapping matrix.
- Control-account register.
- Report rollup tree.
- Missing-mapping checklist.

## References

- `references/industry-coa-templates.md`
