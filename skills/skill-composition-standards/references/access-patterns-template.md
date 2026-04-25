# Access Patterns Template

Produced by `database-design-engineering`. Consumed by `api-design-first` (shapes the API contract) and `observability-monitoring` (shapes query-performance SLOs).

## Template

```markdown
# Access patterns — <bounded context>

**Owner:** <team>

## Read patterns

| ID | Pattern | Primary entity | Filters | Latency target p95 | Frequency | Index required |
|---|---|---|---|---|---|---|
| R1 | Customer views own order list | order | tenant_id, customer_id | 100ms | high (per session) | (tenant_id, customer_id, created_at desc) |
| R2 | Customer views single order | order | id, tenant_id | 50ms | medium | pk |
| R3 | Support searches orders | order | tenant_id, status, created_at range | 500ms | low | (tenant_id, status, created_at) |
| R4 | Admin reports active orders | order | tenant_id, status != 'delivered' | 2s | batch | partial idx (tenant_id, status) where status != 'delivered' |
| R5 | Warehouse list unshipped | order | tenant_id, status = 'paid' | 300ms | medium | partial idx |

## Write patterns

| ID | Pattern | Primary entity | Frequency | Concurrency | Idempotency |
|---|---|---|---|---|---|
| W1 | Place order | order + order_line | high | per-customer serial | Idempotency-Key header; unique constraint on (customer_id, idempotency_key) |
| W2 | Mark paid | order | medium | single-writer (payment webhook) | event id deduplication |
| W3 | Cancel order | order | low | per-order serial | status-transition check |
| W4 | Ship order | order | medium | per-order serial | status-transition check |

## Batch / scheduled patterns

| ID | Pattern | Frequency | Duration budget | Locking |
|---|---|---|---|---|
| B1 | Archive delivered > 7 years | monthly | < 30m | chunked, no global locks |
| B2 | Reindex search | daily | < 1h | read from replica |

## Hot paths

Critical flow (from critical-flow table):

- CF-03 checkout uses W1 + R2.
- CF-01 sign-in uses no queries in this context.

Hot paths must have:

- p95 latency target met by an index that handles the filter selectivity.
- Query plan verified with representative data volume.
- Rollout gate: if EXPLAIN shows seq scan on hot path, reject the release.

## Expected volume

| Entity | Row count | Growth / month |
|---|---|---|
| order | 10M | 200K |
| order_line | 50M | 1M |

## Query plan sanity checks

Before any release:

- Run `EXPLAIN ANALYZE` on R1–R5 with 90th-percentile parameter sets.
- Confirm all hot paths use index scans, not seq scans.
- No filter reduces rows from > 1M to < 10K without an index.

## Revision log

| Date | Change | Author |
|---|---|---|
| YYYY-MM-DD | initial | ... |
```

## Rules

1. Every read pattern has a latency target and frequency class.
2. Every write pattern has a concurrency model and idempotency strategy.
3. Hot paths are flagged explicitly.
4. Batch patterns have a duration budget and locking behaviour.
5. Expected row counts are stated so index strategy is realistic.
6. Query plans are verified before release.

## Common failures

- **Patterns listed without latency targets.** No basis to choose between index strategies.
- **Idempotency ignored on write patterns.** Retries double-write.
- **No hot-path flag.** Team optimises the wrong queries.
- **Batch patterns hold table locks.** A nightly job stalls the whole service for hours.
- **Expected volume guessed, not measured.** Indexes don't hold at real scale.
