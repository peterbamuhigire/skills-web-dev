---
name: api-design-first
description: Use when designing or building APIs — REST conventions, OpenAPI 3 spec-first
  workflow, versioning, authentication, rate limiting, caching (ETags), security headers,
  CORS, HATEOAS, breaking changes, health checks, and GraphQL decision guide...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# API Design First

<!-- dual-compat-start -->
## Use When

- Use when designing or building APIs — REST conventions, OpenAPI 3 spec-first workflow, versioning, authentication, rate limiting, caching (ETags), security headers, CORS, HATEOAS, breaking changes, health checks, and GraphQL decision guide...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `api-design-first` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

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
## Load Alongside

- `world-class-engineering` for shared release gates.
- `system-architecture-design` when the API defines service or module boundaries.
- `database-design-engineering` when resource design drives schema choices.
- `vibe-security-skill` for endpoint security review.

## Overview

Design-first means writing the OpenAPI spec BEFORE writing code. The spec is the contract — it drives client SDKs, documentation, and server validation simultaneously.

**Core principle:** The spec is the source of truth. Code implements the spec, never the other way around.

## Design Workflow

1. Define consumers, latency expectations, and trust boundaries.
2. Model resources and actions around business concepts, not controller names.
3. Write the OpenAPI contract, including auth, validation, errors, and pagination.
4. Prove tenancy, authorization, and idempotency rules before implementation.
5. Design observability: request IDs, audit events, deprecation path, and rate-limit telemetry.
6. Validate that the API can evolve without breaking current consumers.

---

## Additional Guidance

Extended guidance for `api-design-first` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `REST Conventions`
- `Security Headers (Mandatory on All Responses)`
- `OpenAPI 3.1 Spec-First`
- `API Versioning`
- `HTTP Caching (ETags)`
- `HATEOAS Links`
- `Authentication Patterns`
- `Rate Limiting`
- `Pagination`
- `Middleware Order`
- `Health Check Endpoint`
- `GraphQL: When to Use vs REST`
- Additional deep-dive sections continue in the reference file.
