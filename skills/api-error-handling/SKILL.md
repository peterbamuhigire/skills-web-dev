---
name: api-error-handling
description: Comprehensive, standardized error response system for PHP REST APIs with
  SweetAlert2 integration. Use when building REST APIs that need consistent error
  formatting, specific error message extraction from database exceptions, validation
  error...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# API Error Handling
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Comprehensive, standardized error response system for PHP REST APIs with SweetAlert2 integration. Use when building REST APIs that need consistent error formatting, specific error message extraction from database exceptions, validation error...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `api-error-handling` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references, examples` only as needed.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Error response contract | Markdown doc listing canonical error shapes, HTTP codes, and SweetAlert2 mapping | `docs/api/error-contract.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- Use the `examples/` directory for concrete patterns when implementation shape matters.
<!-- dual-compat-end -->
Implement comprehensive, standardized error response system for PHP REST APIs with consistent JSON envelopes, specific error message extraction, and SweetAlert2 integration.

**Core Principles:**

- Consistent JSON envelope across all endpoints
- Specific error messages extracted from all exception types
- Appropriate HTTP status codes for all error categories
- Machine-readable error codes for programmatic handling
- Human-readable messages for SweetAlert2 display
- Secure error handling (no stack traces in production)
- Comprehensive logging with request IDs
- **CRITICAL: Always show error messages to users in SweetAlert (never silent failures)**

**Security Baseline (Required):** Always load and apply the **Vibe Security Skill** for PHP API work. Do not leak sensitive data in responses or logs.

**Cross-Platform:** APIs deploy to Windows (dev), Ubuntu (staging), Debian (production), all running MySQL 8.x. Use `utf8mb4_unicode_ci` collation. Match file/directory case exactly in require paths (Linux is case-sensitive). Use forward slashes in paths.

**See subdirectories for:**

- `references/` - Complete PHP classes (ApiResponse, ExceptionHandler, Exceptions)
- `examples/` - Full endpoint implementation, frontend client

## Additional Guidance

Extended guidance for `api-error-handling` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Response Envelope Standard`
- `HTTP Status Codes`
- `ApiResponse Helper (Quick Reference)`
- `Exception Handler (Quick Reference)`
- `Custom Exception Classes`
- `API Bootstrap Pattern`
- `Endpoint Implementation Pattern`
- `Frontend Integration`
- `Critical Error Display Pattern`
- `Debugging Data Shape Mismatches`
- `API Contract Validation (Frontend-Backend Alignment)`
- `Error Message Extraction`
- Additional deep-dive sections continue in the reference file.