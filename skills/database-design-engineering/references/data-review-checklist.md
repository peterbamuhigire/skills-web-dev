# Data Review Checklist

Use this checklist when proposing or reviewing schemas.

## Modeling

- What business fact does each table or collection represent?
- What state transitions are allowed?
- What data is authoritative versus derived?

## Integrity

- What must be unique?
- What must never be null?
- What relationships must always exist?
- What concurrency issues can violate correctness?

## Querying

- What are the hottest reads?
- What are the hottest writes?
- What filters, joins, and sorts dominate?
- Which queries need pagination, precomputation, or async export?

## Operations

- How will this be migrated in production?
- How will old rows be archived or deleted?
- How will corruption or drift be detected?
- What metrics show that this model is failing at scale?
