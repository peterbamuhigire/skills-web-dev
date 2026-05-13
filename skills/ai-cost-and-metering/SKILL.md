---
name: ai-cost-and-metering
description: >-
  Use when modeling, metering, attributing, billing, or controlling AI usage costs across tenants, plans, features, providers, and agent workloads.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Cost And Metering
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->

## Use When

- Design AI usage metering, cost attribution, quotas, chargeback, or billing controls.
- Model AI cost by tenant, feature, provider, model, request, or agent task.
- Connect cost evidence to plan limits, entitlement enforcement, and customer-facing billing.

## Do Not Use When

- The work is not AI-specific or agentic-AI-specific.
- A narrower retained AI parent skill fits the request better.

## Required Inputs

- Product, tenant, user, data, risk, and operational context relevant to the AI workflow.
- Target artifact: design, implementation plan, audit, test strategy, UX flow, commercial policy, or runbook.
- Constraints from security, privacy, reliability, billing, support, and compliance stakeholders when relevant.

## Workflow

1. Read this SKILL.md first.
2. Load [references/routing.md](references/routing.md) to select the absorbed child reference that matches the task.
3. Load only the selected child reference files needed for the current request.
4. Produce execution-oriented output with assumptions, risks, evidence, and next actions where relevant.

## Quality Standards

- Keep routing explicit: name which reference files were used when the work depends on absorbed material.
- Preserve tenant isolation, auditability, cost controls, safety gates, and operational evidence when they matter.
- Prefer concrete contracts, checklists, tables, schemas, runbooks, and decision records over broad summaries.

## Anti-Patterns

- Loading every absorbed reference by default.
- Treating AI-specific billing, compliance, safety, or UX concerns as generic SaaS work without checking AI failure modes.
- Hiding retired skill names; old slugs must remain discoverable through [references/routing.md](references/routing.md).

## Outputs

- A concrete deliverable matched to the request: architecture, implementation plan, audit, policy, runbook, UX flow, test strategy, or operating model.
- The selected consolidated reference files and any assumptions, risks, evidence requirements, or follow-up actions that affect execution.
## References

- [references/routing.md](references/routing.md) maps retired child skill slugs to their consolidated reference folders.

## Consolidated Child References

- Load [references/routing.md](references/routing.md) to map retired AI child skill slugs to their reference modules.
<!-- dual-compat-end -->
