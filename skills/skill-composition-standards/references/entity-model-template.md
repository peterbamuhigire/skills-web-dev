# Entity Model Template

Produced by `database-design-engineering`. Consumed by `api-design-first`, any service-implementation skill, and `advanced-testing-strategy` (for fixtures).

## Template

```markdown
# Entity model — <bounded context>

**Owner:** <team>
**Engine:** PostgreSQL 16 | MySQL 8 | ...
**Tenancy strategy:** shared schema with tenant_id | schema-per-tenant | DB-per-tenant

## Entities

### `order`

- **Grain:** one row per placed order
- **Lifecycle:** created → paid → shipped → delivered | cancelled
- **Invariants:**
  - `total_amount` = sum of line items at time of creation (frozen)
  - `paid_at` set iff status ∈ {paid, shipped, delivered}
  - `cancelled_at` set iff status = cancelled; mutually exclusive with shipped

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| id | uuid | no | gen_random_uuid() | primary key |
| tenant_id | bigint | no | — | foreign key tenant.id; RLS anchor |
| customer_id | uuid | no | — | fk customer.id |
| status | text | no | 'created' | enum-like; see invariants |
| currency | char(3) | no | — | ISO 4217 |
| total_amount | numeric(12,2) | no | — | frozen at creation |
| created_at | timestamptz | no | now() | |
| paid_at | timestamptz | yes | — | |
| shipped_at | timestamptz | yes | — | |
| delivered_at | timestamptz | yes | — | |
| cancelled_at | timestamptz | yes | — | |
| updated_at | timestamptz | no | now() | trigger updates on change |

- **Indexes:**
  - pk(id)
  - idx(tenant_id, customer_id, created_at desc) — customer order history
  - idx(tenant_id, status) where status != 'delivered' — operational queries
  - idx(tenant_id, created_at) — admin reports

- **Referential integrity:**
  - fk customer_id → customer(id), on delete: restrict
  - fk tenant_id → tenant(id), on delete: restrict

- **Row-level security (if applicable):**
  - policy tenant_isolation: using (tenant_id = current_setting('app.tenant_id')::bigint)

### `order_line`

- **Grain:** one row per item in an order
- **Invariants:**
  - Lines are immutable once the order is paid.
  - Sum of line.total = order.total_amount.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| id | uuid | no | gen_random_uuid() | |
| order_id | uuid | no | — | fk order.id |
| sku | text | no | — | snapshot of product.sku at creation |
| quantity | int | no | — | > 0 |
| unit_price | numeric(12,2) | no | — | frozen at creation |
| line_total | numeric(12,2) | no | — | generated: quantity * unit_price |

...

## Relationships (summary)

```text
tenant 1 -- n customer
tenant 1 -- n order
customer 1 -- n order
order 1 -- n order_line
```

## Data lifecycle

| Entity | Retention | After retention |
|---|---|---|
| order (delivered) | 7 years | archive to cold storage, delete from hot |
| order (cancelled) | 2 years | delete |
| audit_log | 3 years | archive |

## Migration plan

Migrations are numbered sequentially. Each must be additive-first; destructive changes happen in a later migration after all consumers have moved.

See `migration-plan-<context>.md`.

## Revision log

| Date | Change | Author |
|---|---|---|
| YYYY-MM-DD | initial | ... |
```

## Rules

1. Every entity has a stated grain, lifecycle, and invariants.
2. Every column has a nullability and default that matches real semantics (not "null allowed just in case").
3. Every foreign key has an explicit on-delete behaviour.
4. Multi-tenant entities include `tenant_id` and are protected by RLS or application-layer enforcement.
5. Money uses `numeric(p,s)` (Decimal), never `float` or `double`.
6. Timestamps are always `timestamptz` (or equivalent); never naive.
7. Retention is defined per entity.

## Common failures

- **No invariants stated.** Readers have to infer which transitions are legal.
- **Nullable everywhere "just in case".** Loses integrity.
- **Money as `float`.** Rounding errors accumulate. Use Decimal.
- **No indexes listed.** Performance is an afterthought.
- **Cascading deletes on user data.** One bad query cascades into a catastrophe. Default: restrict.
- **No tenancy strategy.** Cross-tenant leaks are the default.
