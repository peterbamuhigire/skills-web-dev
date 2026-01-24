-- Table Partitioning Strategies for Large-Scale SaaS
-- Examples for tenant isolation and time-series data

-- =============================================================================
-- HASH Partitioning - Multi-Tenant Isolation
-- =============================================================================

-- Distribute tenant data across partitions for better performance
CREATE TABLE transactions (
  id BIGINT NOT NULL AUTO_INCREMENT,
  tenant_id INT UNSIGNED NOT NULL,
  user_id INT UNSIGNED NOT NULL,
  amount DECIMAL(13, 2) NOT NULL,
  currency CHAR(3) NOT NULL DEFAULT 'UGX',
  status ENUM('pending', 'completed', 'failed') NOT NULL,
  created_at DATETIME NOT NULL,

  PRIMARY KEY (tenant_id, id),  -- Must include partition key
  KEY idx_user (tenant_id, user_id),
  KEY idx_created (tenant_id, created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY HASH(tenant_id) PARTITIONS 10;

-- Benefits:
-- - Distributes tenant data evenly across partitions
-- - Queries filtered by tenant_id scan only relevant partition
-- - Parallel processing across partitions

-- Query example (scans only 1 partition):
-- SELECT * FROM transactions WHERE tenant_id = 5 AND created_at > '2024-01-01';

-- =============================================================================
-- RANGE Partitioning - Time-Series Data
-- =============================================================================

-- Partition by date for archival and efficient historical queries
CREATE TABLE event_logs (
  id BIGINT NOT NULL AUTO_INCREMENT,
  tenant_id INT UNSIGNED NOT NULL,
  event_type VARCHAR(50) NOT NULL,
  event_data JSON,
  created_at DATETIME NOT NULL,

  PRIMARY KEY (created_at, id),  -- Must include partition key first
  KEY idx_tenant (tenant_id, created_at DESC),
  KEY idx_type (event_type, created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY RANGE (YEAR(created_at)) (
  PARTITION p_2023 VALUES LESS THAN (2024),
  PARTITION p_2024 VALUES LESS THAN (2025),
  PARTITION p_2025 VALUES LESS THAN (2026),
  PARTITION p_2026 VALUES LESS THAN (2027),
  PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- Benefits:
-- - Queries on recent data scan only recent partitions
-- - Easy to drop old partitions (fast delete without locking entire table)
-- - Archive old data efficiently

-- Query example (scans only p_2025 partition):
-- SELECT * FROM event_logs WHERE created_at BETWEEN '2025-01-01' AND '2025-12-31';

-- Drop old data (instant, no locking):
-- ALTER TABLE event_logs DROP PARTITION p_2023;

-- Add new partition:
-- ALTER TABLE event_logs ADD PARTITION (PARTITION p_2027 VALUES LESS THAN (2028));

-- =============================================================================
-- LIST Partitioning - Regional Data
-- =============================================================================

-- Partition by country or region for geographic distribution
CREATE TABLE customers (
  id BIGINT NOT NULL AUTO_INCREMENT,
  tenant_id INT UNSIGNED NOT NULL,
  country_code CHAR(2) NOT NULL,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (country_code, id),  -- Must include partition key
  UNIQUE KEY uk_email (tenant_id, email),
  KEY idx_tenant (tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY LIST COLUMNS(country_code) (
  PARTITION p_east_africa VALUES IN ('UG', 'KE', 'TZ', 'RW', 'BI'),
  PARTITION p_west_africa VALUES IN ('NG', 'GH', 'SN', 'CI'),
  PARTITION p_southern_africa VALUES IN ('ZA', 'BW', 'ZM', 'ZW'),
  PARTITION p_north_africa VALUES IN ('EG', 'MA', 'DZ', 'TN'),
  PARTITION p_other VALUES IN (DEFAULT)
);

-- Benefits:
-- - Queries by region scan only relevant partition
-- - Regional data isolation
-- - Easier compliance with data residency regulations

-- Query example (scans only p_east_africa partition):
-- SELECT * FROM customers WHERE country_code = 'UG';

-- =============================================================================
-- RANGE COLUMNS Partitioning - Multi-Column Ranges
-- =============================================================================

-- Partition by tenant and date for combined isolation
CREATE TABLE invoices (
  id BIGINT NOT NULL AUTO_INCREMENT,
  tenant_id INT UNSIGNED NOT NULL,
  customer_id INT UNSIGNED NOT NULL,
  invoice_number VARCHAR(50) NOT NULL,
  total_amount DECIMAL(13, 2) NOT NULL,
  status ENUM('draft', 'sent', 'paid', 'voided') NOT NULL,
  invoice_date DATE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (tenant_id, invoice_date, id),
  UNIQUE KEY uk_invoice_number (tenant_id, invoice_number),
  KEY idx_customer (tenant_id, customer_id),
  KEY idx_status (tenant_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY RANGE COLUMNS(tenant_id, invoice_date) (
  PARTITION p_t1_2024 VALUES LESS THAN (1, '2025-01-01'),
  PARTITION p_t1_2025 VALUES LESS THAN (1, '2026-01-01'),
  PARTITION p_t2_2024 VALUES LESS THAN (2, '2025-01-01'),
  PARTITION p_t2_2025 VALUES LESS THAN (2, '2026-01-01'),
  PARTITION p_future VALUES LESS THAN (MAXVALUE, MAXVALUE)
);

-- =============================================================================
-- Subpartitioning - Combined Strategies
-- =============================================================================

-- Partition by tenant (HASH), then by date (RANGE) within each partition
CREATE TABLE order_items (
  id BIGINT NOT NULL AUTO_INCREMENT,
  tenant_id INT UNSIGNED NOT NULL,
  order_id BIGINT NOT NULL,
  product_id INT UNSIGNED NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(13, 2) NOT NULL,
  created_at DATETIME NOT NULL,

  PRIMARY KEY (tenant_id, created_at, id),
  KEY idx_order (tenant_id, order_id),
  KEY idx_product (tenant_id, product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY HASH(tenant_id) PARTITIONS 4
SUBPARTITION BY RANGE (YEAR(created_at))
SUBPARTITION TEMPLATE (
  SUBPARTITION sp_2024 VALUES LESS THAN (2025),
  SUBPARTITION sp_2025 VALUES LESS THAN (2026),
  SUBPARTITION sp_future VALUES LESS THAN MAXVALUE
);

-- Benefits:
-- - Double isolation (by tenant and time)
-- - Very efficient for multi-tenant time-series queries
-- - Combines benefits of both strategies

-- =============================================================================
-- Partition Maintenance
-- =============================================================================

-- View partition information
SELECT
  TABLE_NAME,
  PARTITION_NAME,
  PARTITION_METHOD,
  PARTITION_EXPRESSION,
  TABLE_ROWS,
  AVG_ROW_LENGTH,
  DATA_LENGTH
FROM information_schema.PARTITIONS
WHERE TABLE_SCHEMA = 'saas_platform'
  AND TABLE_NAME = 'transactions'
ORDER BY PARTITION_ORDINAL_POSITION;

-- Reorganize partitions (for HASH/KEY partitioning)
ALTER TABLE transactions REORGANIZE PARTITION p0 INTO (
  PARTITION p0 VALUES LESS THAN (1000),
  PARTITION p1 VALUES LESS THAN (2000)
);

-- Optimize specific partition
ALTER TABLE event_logs OPTIMIZE PARTITION p_2024;

-- Analyze specific partition
ALTER TABLE event_logs ANALYZE PARTITION p_2024, p_2025;

-- Check partition for errors
ALTER TABLE event_logs CHECK PARTITION p_2024;

-- Rebuild partition
ALTER TABLE event_logs REBUILD PARTITION p_2024;

-- =============================================================================
-- Best Practices
-- =============================================================================

-- 1. Always include partition key in PRIMARY KEY (first columns)
-- 2. Use HASH partitioning for even distribution (multi-tenant)
-- 3. Use RANGE partitioning for time-series data
-- 4. Use LIST partitioning for categorical data (regions, types)
-- 5. Limit to 50-100 partitions per table (performance)
-- 6. Prune old partitions instead of DELETE (instant, no locks)
-- 7. Query with partition key when possible (partition pruning)
-- 8. Monitor partition size balance
-- 9. Use EXPLAIN PARTITIONS to verify partition pruning
-- 10. Test queries to ensure they benefit from partitioning

-- Example query analysis:
EXPLAIN PARTITIONS
SELECT * FROM transactions
WHERE tenant_id = 5
  AND created_at > '2025-01-01';
-- Should show "partitions: p5" (only scanning 1 partition)

-- =============================================================================
-- When NOT to Use Partitioning
-- =============================================================================

-- ✗ DON'T partition if:
-- - Table has < 1 million rows (overhead not worth it)
-- - Queries don't filter by partition key
-- - Need full table scans frequently
-- - Partition key changes frequently (reorganization overhead)

-- ✓ DO partition if:
-- - Table has > 10 million rows
-- - Queries filter by partition key (tenant_id, date range)
-- - Need to archive/delete old data efficiently
-- - Multi-tenant isolation benefits performance
