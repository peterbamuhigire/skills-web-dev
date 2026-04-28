---
name: demand-forecasting
description: Use for demand forecasts, stockout timing, reorder logic, branch/product sales aggregation, duplicate rows from SQL joins, or demand-driven planning from operational data.
---

# Demand Forecasting

## Overview

Use this skill to turn sales, inventory, branch, and operational signals into demand forecasts and replenishment recommendations. It is especially relevant when fixing SQL joins that duplicate products, deriving days until stockout, or documenting demand-driven planning assumptions.

## Workflow

1. Define the reporting grain first: usually one row per product per shop, branch, outlet, or warehouse for the forecast horizon.
2. Aggregate sales and stock movements before joining product, branch, and stock-balance tables. Do not join raw sales lines directly to item master or stock balances when the output expects one product row.
3. Exclude or separately flag voided sales, returns, internal transfers, stockout days, and one-off events that would distort demand.
4. Normalize demand to a daily rate. Use 7, 30, and 90 day windows when available, and explain which window drives the forecast.
5. Derive days until stockout as `current_stock / daily_demand`. If demand is zero, report "no active demand" rather than hiding the value as an unexplained N/A.
6. Calculate forecast consumption as `daily_demand * horizon_days`.
7. Calculate reorder point as `daily_demand * lead_time_days + safety_stock`.
8. Calculate suggested order as `max(0, forecast_consumption + safety_stock - current_stock - inbound_qty)`.
9. Backtest against historical periods using WAPE/MAPE, bias, and missed-stockout counts.

## Join Guardrails

- Use CTEs or subqueries for `sales_by_product_branch`, `stock_by_product_branch`, and `inbound_by_product_branch`.
- Group every CTE by the same business key before joining: product id plus branch/shop/outlet/warehouse id.
- Join product and branch names once, after aggregation.
- Assert that the final result has no duplicate product plus branch rows.
- If the UI needs one product row per selected branch, collapse variants after filtering by branch, not across all branches.

## References

Load `references/demand_forecasting.md` for SQL templates, stockout formulas, and demand-driven planning notes.
