# Naming Convention — docs/plans

## Hierarchy Rules
- Specs live under: `docs/plans/[domain-or-module]/[feature-name].md`
- **domain-or-module** must be a **core business entity**:
  - Examples: `billing`, `inventory`, `auth`, `assets`, `finance`, `sales`, `hr`
- **feature-name** should be kebab-case and descriptive:
  - Example: `user-profile-update`, `invoice-approval-flow`

## Examples
- `docs/plans/auth/user-profile-update.md`
- `docs/plans/inventory/stock-reorder-alerts.md`
- `docs/plans/billing/refund-processing.md`
