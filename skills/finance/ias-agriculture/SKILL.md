---
name: ias-agriculture
description: Agriculture and biological-asset accounting under IAS 41 (full IFRS) and Section 34 (IFRS for SMEs). Recognition, measurement at fair value less costs to sell where reliably measurable, point-of-harvest treatment, bearer biological assets, government grants in agriculture, cost-model fallback, sector-specific build implications for BIRDC, agribusinesses, poultry, dairy, horticulture, plantation, and aquaculture. Use whenever biological assets, agricultural produce, or sector operations like BIRDC, dynagricug, or other Chwezi agribusiness clients are in scope.
---

# Agriculture (Section 34 / IAS 41)

## Overview

A biological asset (a living animal or plant) is measured at fair value less costs to sell at each reporting date, with changes in P&L, **provided fair value can be measured reliably without undue cost or effort**. Where fair value cannot be reliably measured, the cost model applies. Agricultural produce harvested from biological assets is measured at fair value less costs to sell at the point of harvest; thereafter it is treated as inventory under Section 13 / IAS 2.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/ifrs-for-smes-default.md` (Section 34)
- `doctrine/references/full-ifrs-overlay.md` (IAS 41)
- `doctrine/references/chart-of-accounts.md`

## Scope clarifications

- **Biological asset:** living plant or animal (e.g. poultry, dairy cattle, fish, fruit trees in bearer mode).
- **Agricultural produce:** the harvested product of biological assets (e.g. eggs, milk, fish at landing, fruit at picking).
- **Bearer biological asset (full IFRS):** a plant grown for the production of agricultural produce over more than one period and where the likelihood of being sold as produce is remote (e.g. mature fruit trees). Under IAS 41 amended, bearer plants are accounted for under IAS 16 (PPE), not IAS 41. Section 34 retains the older treatment under fair-value-where-measurable.
- **Government grants** to agriculture: Section 34 (IFRS for SMEs) and IAS 20 / IAS 41 (full IFRS) — recognised as income when conditions met.

## Measurement

| Item | Default | Fallback |
|---|---|---|
| Biological asset | Fair value less costs to sell, with changes in P&L. | Cost less accumulated depreciation and impairment if fair value cannot be reliably measured. |
| Agricultural produce at point of harvest | Fair value less costs to sell. | None — harvested produce always at fair value at harvest under both standards. |
| Agricultural produce post-harvest | Inventory at Section 13 / IAS 2 (cost or NRV). | n/a |
| Bearer plants (full IFRS) | PPE under IAS 16 (cost or revaluation). | n/a |
| Bearer plants (IFRS for SMEs) | Section 34 fair-value where measurable; otherwise cost. | |

## Build implications

### Biological-asset register

- Asset type (animal, plant), species, breed / variety.
- Stage / age class.
- Cohort identifier.
- Location.
- Acquisition date / birth / planting date.
- Cost basis (where cost model).
- Fair-value source and method per reporting date.
- Mortality / loss events linked to journals.
- Custodian / stockperson.

### Cohort-level posting

Postings are typically at cohort level (e.g. "Layer Flock 2026-Q1") rather than per individual animal — but individual events (death, sale, transfer) update the cohort count and value.

### Fair-value re-measurement journal

At each reporting date, the system re-measures and posts the fair-value change to P&L (Gain / Loss from change in fair value of biological assets).

### Harvest event

At harvest:

- Fair value of harvested produce recognised in inventory (Dr Inventory — Agricultural Produce).
- Corresponding credit to Gain on agricultural produce — initial recognition (P&L).
- Biological-asset value adjusts for removed produce.

### Sale of produce

Standard revenue recognition; cost of sale releases the inventory.

### Government grants

A grant attached to a biological asset:

- Unconditional and recognised when receivable (Section 34 / IAS 41 specific).
- Conditional: recognised when conditions are met.
- Grant linked to a biological asset measured at cost: presented under IAS 20 (full IFRS) or Section 24 (SMEs).

## CoA implications

Sector overlay accounts (added in agribusiness entities):

| Code | Name |
|---|---|
| 1750 Biological Assets — Layer Flock | (sub-class as needed) |
| 1751 Biological Assets — Broilers | |
| 1752 Biological Assets — Dairy Herd | |
| 1753 Biological Assets — Fish Stock | |
| 1754 Bearer Plants — Coffee | (where IFRS 16 / IAS 16 treatment applies) |
| 1500 Inventory — Agricultural Produce — Eggs | |
| 1501 Inventory — Agricultural Produce — Milk | |
| 1502 Inventory — Agricultural Produce — Fish | |
| 7200 Gain / (Loss) — Change in FV of Biological Assets | P&L. |
| 7210 Gain / (Loss) — Mortality / Loss of Biological Assets | P&L. |
| 4400 Other Operating Income — Government Grants | Where presented gross. |

## Disclosures

- Description of each group of biological assets.
- Methods and assumptions for fair-value determination.
- Reconciliation of carrying amount (cohort movements, FV changes, sales, harvests, mortality).
- Restrictions on title and pledges.
- Commitments for the development or acquisition of biological assets.
- Financial-risk management for biological assets.
- Government grants recognised and unfulfilled conditions.

## Sector-specific guidance

### Poultry (BIRDC, similar)

- Cohorts by hatch date.
- Layers: fair value as a producing asset; eggs at harvest treated as agricultural produce → inventory.
- Broilers: typically short cycle; cost model often more practical; sale at FV less costs to sell at point of sale.
- Mortality: regular events; thresholds for write-down.

### Dairy

- Cohorts by milking parity / age.
- Milk at point of harvest at FV less costs to sell.

### Fish

- Cohorts by stocking date.
- Harvest event at landing.

### Plantation crops (coffee, tea)

- Bearer plants under IAS 16 / Section 34 fair-value where measurable.
- Annual crops as biological assets.
- Harvest event at picking.

## Forbidden patterns

- Mixing biological assets and inventory accounting before the point of harvest (blocker).
- Cost model applied to biological assets when fair value is reliably measurable (major).
- LIFO applied to agricultural produce (blocker).
- Mortality not recognised in the period it occurred (major).
- Government grants netted against biological-asset cost without disclosure (major where material).

## Acceptance evidence

- Biological-asset register with cohort and event log.
- Fair-value methodology document with reviewer sign-off.
- Reconciliation note generator.
- Harvest-event journals tested.
- Government-grant treatment documented.

## Files

- `SKILL.md`.
- `references/fair-value-methodology.md` — common FV approaches for poultry, dairy, fish, plantation crops.
- `references/cohort-data-model.md`.
- `examples/birdc-layer-flock-q2-2026.md` — worked example.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
