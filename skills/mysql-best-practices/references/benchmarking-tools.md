# MySQL Benchmarking & Capacity Planning Tools

Production tools for measuring MySQL performance, identifying bottlenecks, and planning capacity.

**Source:** Garcia (2023) Ch7 identified this gap; tool documentation based on official sources.

---

## Tool Overview

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **SysBench** | OLTP workload simulation | Capacity planning, hardware comparison, config tuning validation |
| **mysqlslap** | Quick query benchmarks | Compare query alternatives, test index impact |
| **pt-query-digest** | Slow query analysis | Production query profiling (already in query-performance.md) |
| **MySQL Shell \util** | Parallel dump/load benchmarks | Migration and backup performance |

---

## SysBench — OLTP Workload Simulation

The standard tool for MySQL load testing. Simulates real OLTP workloads with configurable concurrency.

### Installation

```bash
# Ubuntu/Debian
sudo apt install sysbench

# CentOS/RHEL
sudo yum install sysbench

# macOS
brew install sysbench

# Verify
sysbench --version
```

### Step 1: Prepare Test Data

```bash
# Create test database first
mysql -u root -e "CREATE DATABASE sbtest CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Prepare 10 tables with 1M rows each (adjust to match production data size)
sysbench /usr/share/sysbench/oltp_read_write.lua \
  --mysql-host=127.0.0.1 \
  --mysql-port=3306 \
  --mysql-user=root \
  --mysql-password='' \
  --mysql-db=sbtest \
  --tables=10 \
  --table-size=1000000 \
  prepare
```

### Step 2: Run OLTP Read/Write Benchmark

```bash
# Simulate 16 concurrent threads for 300 seconds
sysbench /usr/share/sysbench/oltp_read_write.lua \
  --mysql-host=127.0.0.1 \
  --mysql-port=3306 \
  --mysql-user=root \
  --mysql-password='' \
  --mysql-db=sbtest \
  --tables=10 \
  --table-size=1000000 \
  --threads=16 \
  --time=300 \
  --report-interval=10 \
  run
```

### Step 3: Read Key Metrics

```
SQL statistics:
    queries performed:
        read:    1,247,604
        write:   356,458
        other:   178,229
        total:   1,782,291
    transactions: 89,114 (297.02 per sec.)
    queries:      1,782,291 (5940.46 per sec.)

Latency (ms):
         min:     2.14
         avg:    53.83
         max:   412.76
         95th:  127.81
```

**Key metrics to record:**
- **Transactions/sec (TPS):** Primary throughput metric
- **Queries/sec (QPS):** Total query throughput
- **95th percentile latency:** User-experienced worst case (P95)
- **Max latency:** Absolute worst case

### Step 4: Clean Up

```bash
sysbench /usr/share/sysbench/oltp_read_write.lua \
  --mysql-db=sbtest --mysql-user=root cleanup
```

### Common SysBench Workloads

| Workload | Script | Use Case |
|----------|--------|----------|
| Read/Write mix | `oltp_read_write.lua` | General OLTP (default choice) |
| Read-only | `oltp_read_only.lua` | Read-replica testing |
| Write-only | `oltp_write_only.lua` | Write-heavy workload testing |
| Point select | `oltp_point_select.lua` | Index lookup performance |
| Insert | `oltp_insert.lua` | Bulk insert throughput |

### Concurrency Scaling Test

Test how MySQL handles increasing load — find the throughput ceiling:

```bash
# Run at 1, 2, 4, 8, 16, 32, 64, 128 threads
for threads in 1 2 4 8 16 32 64 128; do
  echo "=== Testing with $threads threads ==="
  sysbench /usr/share/sysbench/oltp_read_write.lua \
    --mysql-host=127.0.0.1 --mysql-user=root --mysql-db=sbtest \
    --tables=10 --table-size=1000000 \
    --threads=$threads --time=120 --report-interval=10 \
    run 2>&1 | grep -E "(transactions:|95th)"
done
```

**Expected pattern:** TPS increases linearly up to CPU core count, then plateaus, then degrades. The plateau point is your concurrency limit.

```
Threads:   1    2    4    8    16   32   64   128
TPS:      50  100  195  370  680  720  690  580  ← degradation starts at 64
```

---

## mysqlslap — Quick Query Benchmarks

Built into MySQL. Best for quick A/B comparisons of query alternatives or index impact.

### Compare Two Query Approaches

```bash
# Test query A: subquery
mysqlslap \
  --host=127.0.0.1 --user=root \
  --create-schema=saas_platform \
  --query="SELECT id FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE status = 'active') LIMIT 100;" \
  --concurrency=10 --iterations=50 --no-drop

# Test query B: JOIN (should be faster)
mysqlslap \
  --host=127.0.0.1 --user=root \
  --create-schema=saas_platform \
  --query="SELECT o.id FROM orders o JOIN customers c ON o.customer_id = c.id WHERE c.status = 'active' LIMIT 100;" \
  --concurrency=10 --iterations=50 --no-drop
```

### Output Interpretation

```
Benchmark
    Average number of seconds to run all queries: 0.234 seconds
    Minimum number of seconds to run all queries: 0.189 seconds
    Maximum number of seconds to run all queries: 0.412 seconds
    Number of clients running queries: 10
    Average number of queries per client: 1
```

### Test Index Impact

```bash
# Before index
mysqlslap --user=root --create-schema=saas_platform \
  --query="SELECT * FROM orders WHERE tenant_id = 1 AND status = 'pending' ORDER BY created_at DESC LIMIT 25;" \
  --concurrency=20 --iterations=100 --no-drop

# Add index
mysql -u root saas_platform -e "ALTER TABLE orders ADD INDEX idx_tenant_status_created (tenant_id, status, created_at DESC);"

# After index — compare times
mysqlslap --user=root --create-schema=saas_platform \
  --query="SELECT * FROM orders WHERE tenant_id = 1 AND status = 'pending' ORDER BY created_at DESC LIMIT 25;" \
  --concurrency=20 --iterations=100 --no-drop
```

---

## Capacity Planning Methodology

### Step 1: Baseline Current Performance

```sql
-- Record current production metrics
SELECT
    VARIABLE_NAME, VARIABLE_VALUE
FROM performance_schema.global_status
WHERE VARIABLE_NAME IN (
    'Questions', 'Com_select', 'Com_insert', 'Com_update', 'Com_delete',
    'Threads_connected', 'Threads_running',
    'Innodb_buffer_pool_read_requests', 'Innodb_buffer_pool_reads',
    'Innodb_row_lock_waits', 'Slow_queries'
);

-- Buffer pool hit rate (must be > 99%)
SELECT
    ROUND((1 - (
        (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads') /
        (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Innodb_buffer_pool_read_requests')
    )) * 100, 2) AS buffer_pool_hit_rate_pct;
```

### Step 2: Calculate Growth Projections

```
Current daily QPS peak: 500
Monthly growth rate: 15%
Months to plan for: 12

Projected peak QPS = 500 * (1.15)^12 = 2,672 QPS

Current server max (from SysBench): 3,000 TPS
Headroom needed: 30% (never exceed 70% capacity)
Effective max: 3,000 * 0.70 = 2,100 TPS

Result: Need capacity upgrade within 8 months
```

### Step 3: Test Upgrade Scenarios with SysBench

Run SysBench on candidate configurations:
- Current server vs upgraded server
- Current config vs tuned config (larger buffer pool, more connections)
- Single server vs read replica

### Step 4: Set Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| QPS (% of tested max) | 60% | 80% |
| P95 query latency | 2x baseline | 5x baseline |
| Buffer pool hit rate | < 99% | < 97% |
| Threads running | > 2x CPU cores | > 4x CPU cores |
| Slow queries/min | > 10 | > 50 |
| Disk I/O utilisation | > 60% | > 85% |

---

## Benchmarking Best Practices

1. **Match production data size** — benchmark with realistic data volumes. 1K rows benchmarks mean nothing for 10M row tables.
2. **Test at sustained load** — run benchmarks for 5+ minutes minimum. Short bursts hide thermal throttling and buffer pool warming.
3. **Warm the buffer pool first** — run a warmup pass before measuring. Cold-start numbers are misleading.
4. **Isolate the variable** — change one thing at a time (config, index, query). Multiple changes make results unattributable.
5. **Record everything** — server specs, MySQL version, config, data size, thread count, duration. Benchmarks without context are useless.
6. **Test on production-equivalent hardware** — laptop SSDs behave differently from cloud EBS volumes.

---

## Quick Reference Commands

```bash
# SysBench: Quick 60-second OLTP test
sysbench oltp_read_write --mysql-user=root --mysql-db=sbtest \
  --tables=4 --table-size=100000 --threads=8 --time=60 run

# mysqlslap: Quick 10-client test of a specific query
mysqlslap --user=root --create-schema=mydb \
  --query="SELECT COUNT(*) FROM orders WHERE tenant_id=1;" \
  --concurrency=10 --iterations=50 --no-drop

# pt-query-digest: Analyse slow log (see query-performance.md for details)
pt-query-digest /var/log/mysql/slow.log --order-by Query_time:sum --limit 10
```

---

*Reference for mysql-best-practices skill. Source: Garcia (2023) gap analysis.*
