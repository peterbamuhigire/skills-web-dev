# ADR Template

Architecture Decision Record. One ADR captures one structural decision, the alternatives considered, and the reasoning.

## When to write an ADR

- A decision will be hard or expensive to reverse.
- The decision is non-obvious and future engineers will ask "why did we do it this way?"
- Two or more alternatives had plausible cases.

Do not write ADRs for trivial or reversible choices.

## Template

```markdown
# ADR-NNNN: <title in imperative, e.g., "Use Postgres rather than MongoDB for the orders service">

- **Status:** proposed | accepted | superseded by ADR-MMMM | deprecated
- **Date:** YYYY-MM-DD
- **Deciders:** <names>
- **Consulted:** <names>
- **Informed:** <names>

## Context

<One or two paragraphs. What problem are we solving? What constraints apply? What is already true about the system? No solutions yet.>

## Decision

<One or two sentences stating what we will do.>

## Alternatives considered

### Alternative A — <name>

- Pros: <bullets>
- Cons: <bullets>
- Rejected because: <reason>

### Alternative B — <name>

- Pros: <bullets>
- Cons: <bullets>
- Rejected because: <reason>

## Consequences

- What becomes easier: <bullets>
- What becomes harder: <bullets>
- What we will need to revisit: <bullets, with trigger conditions>

## Compliance / verification

<How will we know this decision is being followed? Lint rule, review checklist, periodic audit, runtime check?>
```

## File naming

- `docs/adr/NNNN-title-slug.md`
- NNNN is zero-padded (`0001`, `0042`).
- Slug matches the title.
- Sequential across the project.

## Status transitions

- `proposed` — drafted, awaiting review.
- `accepted` — approved and in effect.
- `superseded by ADR-MMMM` — replaced by a newer decision. Include the replacement's number.
- `deprecated` — the decision no longer applies but has not been replaced (e.g., the module it covered was removed).

Never delete an ADR. History is part of the value.

## Common failures

- **Decision hidden inside Context.** Readers can't tell what was actually decided.
- **No alternatives.** Either the author didn't consider any, or the ADR was written after the fact to rationalise a choice — both bad.
- **Pros/cons lists without a "rejected because" line.** Leaves the reader guessing why B lost to A.
- **Consequences missing the "harder" column.** Every decision has a cost; name it.
- **No compliance.** If there's no way to tell whether the decision is being followed, it is decoration, not governance.
