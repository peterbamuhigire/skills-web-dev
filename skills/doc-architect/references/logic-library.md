# Logic Library

Common domain constraints to reuse when generating AGENTS.md.

## Currency & Money

- Use fixed-precision decimals (e.g., DECIMAL(19,4))
- Store currency codes as ISO-4217 strings
- Do not use floats for money

## Time & Timezones

- Store all timestamps in UTC
- Convert to local timezone at the edge/UI
- Use explicit timezone fields for locale-specific scheduling

## Soft-Delete Patterns

- Soft-delete with `deleted_at` and `deleted_by`
- Prevent hard deletes for core domain entities
- Require audit logs for destructive operations

## Identity & Keys

- Use immutable primary keys
- Avoid reusing identifiers
- Prefer UUIDs for externally exposed IDs when appropriate

## Audit & Compliance

- Capture create/update metadata (`created_at`, `updated_at`, `created_by`)
- Log security-sensitive changes
- Retain audit logs for regulated data

## Data Quality

- Validate enums at the database and application layers
- Use constraints for bounds (min/max) where possible
- Document nullability and default values explicitly

## Aggregations

- Precompute aggregates for large datasets
- Avoid double-counting by using stable dedup keys
- Define aggregation windows and rounding rules
