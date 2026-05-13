---
name: ai-agent-governance-and-limits
description: >-
  Use when defining agent budgets, step limits, reversibility, blast-radius controls, kill switches, and governance policy for agentic AI systems.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent Governance And Limits
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->

## Use When

- Set step, wallclock, token, model, and cost budgets for agents.
- Define reversibility, blast-radius limits, and safe failure behavior.
- Connect runtime controls to policy, tenant limits, and operational review.

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
