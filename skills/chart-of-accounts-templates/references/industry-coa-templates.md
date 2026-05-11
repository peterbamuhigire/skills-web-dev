# Industry CoA Templates

These are starting templates, not statutory charts. Clone per tenant and verify with the tenant's reporting standard and tax regime.

## Hospitality / Restaurant

- Revenue: food sales, beverage sales, accommodation, service charge, delivery fees.
- COGS: food ingredients, beverages, packaging, delivery direct costs.
- Inventory: food stock, beverage stock, consumables.
- Expenses: rent, utilities, kitchen payroll, front-office payroll, cleaning, repairs, marketing.
- Mappings: menu category -> revenue and COGS; payment method -> cash/bank/mobile money; VAT rate -> output/input VAT.

## Retail

- Revenue: product sales by category, delivery income, discounts/returns contra revenue.
- COGS: merchandise COGS by category.
- Inventory: merchandise by location, goods in transit, inventory write-downs.
- Mappings: SKU category -> revenue/inventory/COGS; supplier type -> AP; stock adjustment reason -> shrinkage, damage, write-down.

## Professional Services

- Revenue: consulting, retainers, implementation, support, reimbursables.
- Cost of service: contractor costs, project labour, direct travel.
- WIP/deferred revenue where contracts require it.
- Mappings: project type -> revenue/cost centre; invoice item -> performance obligation where relevant.

## Manufacturing

- Revenue: finished goods sales, scrap sales.
- Inventory: raw materials, WIP, finished goods, spares.
- COGS: materials, direct labour, factory overhead absorbed, variances.
- Mappings: BOM inputs -> raw materials; production order -> WIP; shipment -> COGS.

## Schools

- Revenue: tuition, boarding, transport, meals, uniforms, exam fees.
- Liabilities: fees paid in advance, deposits.
- Assets: student receivables.
- Expenses: teaching payroll, meals, transport, scholastic materials, maintenance.
- Mappings: fee item -> revenue/deferred revenue; student -> AR subledger tag.

## Clinics / Hospitals

- Revenue: consultation, lab, pharmacy, procedure, inpatient, insurance claims.
- Inventory: medicines, lab reagents, medical supplies.
- AR: patient receivables, insurer receivables.
- Expenses: clinical payroll, pharmacy COGS, lab supplies, medical waste, equipment maintenance.

## NGOs / Fund Accounting

- Net assets/funds: unrestricted, temporarily restricted/designated by donor, project funds.
- Revenue: grants, donations, membership, fundraising events.
- Expenses: program services, administration, fundraising, project direct costs.
- Mappings: donor/project/fund tag -> fund dimension; grant receipt -> deferred or restricted grant liability/net asset treatment based on terms.

## Agribusiness

- Revenue: crop sales, livestock sales, processing income.
- Inventory/biological tracking: inputs, produce on hand, livestock where applicable, feed, veterinary supplies.
- COGS: seed/feed/fertilizer, direct labour, harvesting, processing, packaging.
- Mappings: crop/livestock enterprise -> cost centre; harvest event -> inventory; sale -> revenue/COGS.
