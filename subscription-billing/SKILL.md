---
name: subscription-billing
description: Use when designing or reviewing subscription billing strategy, plan
  lifecycle, dunning, metered billing, tax handling, churn recovery, and SaaS revenue
  metrics. Covers trial-to-paid conversion, upgrades, downgrades, pauses, cancellations,
  usage pricing, and revenue recognition fundamentals.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Subscription Billing

<!-- dual-compat-start -->
## Use When

- Use when designing or reviewing subscription billing strategy, plan lifecycle, dunning, metered billing, tax handling, churn recovery, and SaaS revenue metrics. Covers trial-to-paid conversion, upgrades, downgrades, pauses, cancellations, usage pricing, and revenue recognition fundamentals.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `subscription-billing` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather pricing strategy, customer segments, currencies, entitlement model, tax footprint, and the concrete billing problem to solve; load `references/` only as needed.
- Confirm the desired deliverable: pricing architecture, implementation plan, code, review, migration plan, audit, or documentation.

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

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Use this skill when recurring revenue must be intentional rather than incidental. The goal is to design plans, lifecycle transitions, recovery workflows, and finance signals that support retention, predictable revenue, and trustworthy customer experience.

## Load Order

1. Load `world-class-engineering`.
2. Load `stripe-payments` for Stripe mechanics and webhook integration.
3. Load this skill for plan design, lifecycle, dunning, metering, tax, and reporting.

## Billing Workflow

### 1. Design the Plan Hierarchy

Use a small, understandable set of tiers such as:

- Freemium: low-friction trial of value, strong upgrade prompts
- Starter: single team or low-volume paid entry
- Pro: core commercial plan with the best margin and retention target
- Enterprise: negotiated contracts, invoicing, or custom controls

Principles:

- tie pricing to delivered value, not internal implementation cost alone
- keep downgrade paths real, not punitive traps
- keep feature gates explicit and machine-enforceable
- avoid too many tiers that create choice overload

### 2. Model the Subscription Lifecycle

Support these transitions deliberately:

- free trial to paid
- paid renewal
- immediate upgrade
- downgrade now or downgrade at renewal
- pause or grace period
- cancel at period end
- reactivate or win-back

Keep entitlement state aligned to subscription state and billing dates, not vague support rules.

### 3. Choose Proration and Change Timing

- Prorate upgrades when the user expects immediate extra value.
- Avoid surprise charges on downgrades or plan experimentation.
- Offer “upgrade now” versus “switch at next renewal” when that choice matters.
- Use `none` when the business prefers clean next-cycle transitions over proration complexity.

### 4. Design Dunning and Recovery

- Treat payment failure as a recoverable lifecycle step, not an instant cancellation.
- Define grace periods, retries, in-app warnings, and account restrictions.
- Keep dunning customer-facing, specific, and easy to act on.
- Make sure support, product, and finance agree on the exact suspension and cancellation thresholds.

### 5. Add Metered Billing Only When It Matches Value

Use usage pricing when the customer understands and can monitor the billed unit, for example:

- seats
- API calls
- storage
- messages
- reports generated

Do not use metered pricing for units the customer cannot predict or audit.

### 6. Handle Currency and Tax Deliberately

- Keep the account billing currency explicit in your own data model.
- Use per-currency Prices or Stripe localization features where supported; do not depend on undocumented currency guessing.
- For tax, choose between Stripe Tax and controlled manual tax rates based on footprint and compliance maturity.
- Treat East Africa VAT and withholding tax requirements as finance and legal controls, not just API fields.

### 7. Measure Revenue Health

Track:

- MRR
- ARR
- churn rate
- net revenue retention
- trial conversion rate
- failed-payment recovery rate

Keep metric definitions consistent and tied to the same billing states over time.

## Standards

### Customer Experience

- Billing transitions must be understandable before the charge happens.
- Cancellations should collect useful feedback and offer sensible downgrade or pause options.
- Upgrade prompts should appear at the point of value, not as constant noise.

### Access Control

- Cancelled users should not keep paid access beyond the billed period unless the policy says so explicitly.
- Failed-payment grace windows must be encoded in entitlement logic.
- Reactivation should preserve history and minimize support friction.

### Finance and Data

- Separate cash collection from revenue recognition.
- Keep subscription ledger, invoice ledger, and entitlement ledger reconcilable.
- Revenue metrics should be reproducible from raw billing data, not spreadsheet folklore.

## Review Checklist

- [ ] Plan tiers are understandable and tied to value.
- [ ] Subscription lifecycle transitions are explicit and entitlement-safe.
- [ ] Proration behavior matches user expectations and business policy.
- [ ] Failed-payment dunning and grace periods are encoded clearly.
- [ ] Metered billing uses units customers can understand and monitor.
- [ ] Currency and tax handling are explicit for each target market.
- [ ] MRR, ARR, churn, and NRR definitions are documented consistently.

## References

- [references/dunning-management.md](references/dunning-management.md): Payment-failure recovery flows and suspension logic.
- [references/metered-billing.md](references/metered-billing.md): Usage pricing models, reporting patterns, and billing-cycle resets.
- [references/revenue-recognition.md](references/revenue-recognition.md): Deferred revenue, ratable recognition, and ASC 606 or IFRS 15 basics.
- [../stripe-payments/SKILL.md](../stripe-payments/SKILL.md): Stripe integration, PaymentIntents, subscriptions, portal, and webhooks.
- [../ai-saas-billing/SKILL.md](../ai-saas-billing/SKILL.md): Module-gating and add-on billing alignment for paid capabilities.
