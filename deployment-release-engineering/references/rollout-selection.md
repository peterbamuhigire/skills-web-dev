# Rollout Selection

## Use Rolling When

- change risk is moderate
- rollback speed is less critical
- capacity is limited

## Use Blue-Green When

- rollback speed matters
- clean cutover is preferred
- duplicate capacity is available temporarily

## Use Canary When

- change risk is high
- partial exposure gives useful evidence
- monitoring quality is strong enough to detect regression quickly
