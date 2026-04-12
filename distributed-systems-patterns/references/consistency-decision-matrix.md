# Consistency Decision Matrix

Use this matrix when choosing between synchronous and asynchronous coordination.

## Use Synchronous Coordination When

- the caller must know the result immediately
- the workflow cannot continue safely without confirmation
- the data must be current for the next user-facing step

## Use Asynchronous Coordination When

- the work is slow, bursty, or integration-heavy
- eventual completion is acceptable
- temporary dependency failure should not block the initiating workflow
- backpressure and decoupling are more valuable than immediate consistency

## Use Stronger Consistency When

- money moves
- inventory or entitlement correctness is immediate and user-visible
- legal or compliance guarantees require current truth

## Use Eventual Consistency When

- read freshness can lag safely
- reconciliation is practical
- user experience can explain pending or in-progress state clearly

## Require Extra Design When

- actions must happen exactly once from the business perspective
- ordering changes user-visible correctness
- compensation is expensive or impossible
