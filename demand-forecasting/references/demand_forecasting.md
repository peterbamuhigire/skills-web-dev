# Demand Forecasting Reference

## Demand-Driven Planning

Demand forecasting should start from the customer or outlet signal and work backward into fulfillment. Treat sales, stockouts, promotions, lead times, branch differences, and service goals as the operating model, not as decorations added after a generic forecast.

## Core Formulas

- `daily_demand = units_sold / in_stock_days`
- `days_until_stockout = current_stock / daily_demand`
- `forecast_consumption = daily_demand * horizon_days`
- `safety_stock = demand_stddev * service_level_factor * sqrt(lead_time_days)`
- `reorder_point = daily_demand * lead_time_days + safety_stock`
- `suggested_order_qty = max(0, forecast_consumption + safety_stock - current_stock - inbound_qty)`

If `daily_demand <= 0`, report no active demand and keep stockout risk low unless there is a separate expiry, commitment, or minimum-stock rule.

## SQL Pattern

```sql
WITH sales_daily AS (
  SELECT sl.product_id, s.branch_id, DATE(s.sold_at) AS sale_date, SUM(sl.quantity) AS qty
  FROM sale_lines sl
  JOIN sales s ON s.id = sl.sale_id
  WHERE s.sold_at >= :window_start
    AND s.sold_at < :window_end
    AND s.status NOT IN ('voided', 'refunded', 'cancelled')
  GROUP BY sl.product_id, s.branch_id, DATE(s.sold_at)
),
sales_rollup AS (
  SELECT product_id, branch_id,
    SUM(CASE WHEN sale_date >= CURRENT_DATE - INTERVAL '7 day' THEN qty ELSE 0 END) / 7.0 AS avg_7d,
    SUM(CASE WHEN sale_date >= CURRENT_DATE - INTERVAL '30 day' THEN qty ELSE 0 END) / 30.0 AS avg_30d,
    SUM(CASE WHEN sale_date >= CURRENT_DATE - INTERVAL '90 day' THEN qty ELSE 0 END) / 90.0 AS avg_90d
  FROM sales_daily
  GROUP BY product_id, branch_id
),
stock_rollup AS (
  SELECT product_id, branch_id, SUM(on_hand_qty) AS current_stock, SUM(inbound_qty) AS inbound_qty
  FROM stock_balances
  GROUP BY product_id, branch_id
)
SELECT p.id AS product_id, p.name AS product_name, b.id AS branch_id, b.name AS branch_name,
       COALESCE(st.current_stock, 0) AS current_stock,
       COALESCE(sr.avg_7d, 0) AS avg_7d,
       COALESCE(sr.avg_30d, 0) AS avg_30d,
       COALESCE(sr.avg_90d, 0) AS avg_90d
FROM stock_rollup st
LEFT JOIN sales_rollup sr ON sr.product_id = st.product_id AND sr.branch_id = st.branch_id
JOIN products p ON p.id = st.product_id
JOIN branches b ON b.id = st.branch_id;
```

## Cardinality Checks

```sql
SELECT product_id, branch_id, COUNT(*) AS row_count
FROM forecast_result
GROUP BY product_id, branch_id
HAVING COUNT(*) > 1;
```

This query must return zero rows before the report is accepted.
