---
name: postgresql-server-programming
description: PostgreSQL server-side programming sourced from "PostgreSQL Server Programming"
  (Usama Dar, Packt) and "Introduction to PostgreSQL for the Data Professional". Covers
  PL/pgSQL functions and procedures (structure, variables, error handling, loops,
  cursors), trigger functions (row-level, statement-level, WHEN conditions), event
  triggers (DDL auditing), extensions (creating and publishing), and best practices
  (SOA, DRY, KISS). Companion to postgresql-fundamentals and postgresql-advanced-sql.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PostgreSQL Server Programming

<!-- dual-compat-start -->
## Use When

- PostgreSQL server-side programming sourced from "PostgreSQL Server Programming" (Usama Dar, Packt) and "Introduction to PostgreSQL for the Data Professional". Covers PL/pgSQL functions and procedures (structure, variables, error handling, loops, cursors), trigger functions (row-level, statement-level, WHEN conditions), event triggers (DDL auditing), extensions (creating and publishing), and best practices (SOA, DRY, KISS). Companion to postgresql-fundamentals and postgresql-advanced-sql.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `postgresql-server-programming` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Why Program in the Server

- **Data locality** — avoid network round trips for complex logic
- **Integrity enforcement** — triggers fire regardless of which client writes
- **Security** — grant EXECUTE on functions, deny direct table access
- **Performance** — reduce per-row round trips in batch operations
- **Auditability** — triggers capture changes transparently

Use server-side code for integrity, auditing, and data-local transformation. Keep business logic that requires application context in the application layer.

## PL/pgSQL Function Structure

```sql
CREATE OR REPLACE FUNCTION function_name(param1 type, param2 type)
RETURNS return_type
LANGUAGE plpgsql
AS $$
DECLARE
    var1  data_type := initial_value;
    var2  data_type;
    rec   RECORD;
BEGIN
    -- body
    RETURN result;
END;
$$;
```

### Volatility Categories

| Category | Description | Optimiser Benefit |
|---|---|---|
| `IMMUTABLE` | Same input always gives same output, no DB access | Most aggressive inlining |
| `STABLE` | Same input gives same output within a transaction | Safe for index scans |
| `VOLATILE` (default) | Can return different results or modify data | No optimisation |

```sql
-- Immutable: pure computation
CREATE FUNCTION slugify(text) RETURNS text LANGUAGE sql IMMUTABLE AS $$
    SELECT lower(regexp_replace(regexp_replace($1, '[^a-zA-Z0-9\s-]', '', 'g'), '\s+', '-', 'g'));
$$;

-- Stable: reads DB but doesn't modify it
CREATE FUNCTION get_exchange_rate(currency text) RETURNS numeric LANGUAGE sql STABLE AS $$
    SELECT rate FROM exchange_rates WHERE code = currency;
$$;
```

## Additional Guidance

Extended guidance for `postgresql-server-programming` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Variables and Data Types`
- `Control Flow`
- `Error Handling`
- `Returning Structured Data`
- `Stored Procedures`
- `Trigger Functions`
- `Event Triggers (DDL Auditing)`
- `Cursors`
- `Extensions`
- `Programming Best Practices`
- `Anti-Patterns`
