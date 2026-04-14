# Trunk-Based Delivery

Use this reference when branch strategy is affecting release speed, merge pain, or confidence.

## Core Rules

- Keep branches short-lived and integrated frequently.
- Prefer small merges over large private development islands.
- Use feature flags, config flags, or dark launches to separate integration from exposure.
- Make broken trunk a team priority to repair quickly.

## Warning Signs

- branches that live for many days without integration
- repeated merge surprises near release time
- delayed testing because work stays off trunk too long
- releases that require manual cherry-picking or last-minute conflict cleanup
