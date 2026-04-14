# Test Matrix Template

## Change Summary

- Change
- Risk level
- Critical users or workflows affected
- Rollout method
- Rollback method

## Test Matrix

| Layer | Purpose | Required? | Evidence |
|---|---|---|---|
| Commit stage | Build, lint, unit checks, packaging, static analysis |  |  |
| Unit | Logic and edge cases |  |  |
| Integration | Real boundaries and dependencies |  |  |
| Contract | API or service compatibility |  |  |
| Acceptance | Business workflow at app boundary |  |  |
| End-to-end | Critical workflow confidence |  |  |
| Manual or exploratory | UX, accessibility, platform checks |  |  |

## Open Risks

- What is still unproven?
- What would detect failure quickly after release?
