---
name: dual-auth-rbac
description: Dual authentication system (Session + JWT) with role-based access control
  (RBAC) for multi-tenant applications. Use when implementing secure authentication
  across web UI and API/mobile clients, with franchise/tenant-scoped permissions.
  Works...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Dual Authentication with RBAC

<!-- dual-compat-start -->
## Use When

- Dual authentication system (Session + JWT) with role-based access control (RBAC) for multi-tenant applications. Use when implementing secure authentication across web UI and API/mobile clients, with franchise/tenant-scoped permissions. Works...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `dual-auth-rbac` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Auth + RBAC decision record | Markdown doc per `skill-composition-standards/references/adr-template.md` covering Session vs JWT split and tenant scoping | `docs/auth/dual-auth-adr.md` |
| Security | RBAC permission matrix | Markdown doc mapping roles, modules, and per-action grants | `docs/auth/rbac-matrix.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Implement production-grade dual authentication combining session-based (stateful) and JWT-based (stateless) auth with comprehensive RBAC and multi-tenant isolation.

**Core Principle:** Different clients need different auth strategies. Web UIs benefit from sessions; APIs/mobile need stateless tokens. RBAC must work seamlessly across both.

**Database Standards:** All database schema changes (adding auth tables, stored procedures, indexes) MUST follow **mysql-best-practices** skill migration checklist.

**Deployment:** Runs on Windows dev (MySQL 8.4.7), Ubuntu staging (MySQL 8.x), Debian production (MySQL 8.x). Use `utf8mb4_unicode_ci` collation. Ensure file paths and require statements match exact case for Linux compatibility.

**See references/ for:** `schema.sql` (complete database design with 9 tables)

## When to Use

✅ Multi-tenant SaaS with web + API access
✅ Web UI + mobile apps authentication
✅ Role-based permissions with tenant isolation
✅ Token revocation capability required
✅ Multiple device sessions per user
✅ Three-tier panel architecture (super admin, franchise admin, member portal)

❌ Simple single-tenant apps (overkill)
❌ Read-only public APIs
❌ Internal tools (simpler auth suffices)

## Additional Guidance

Extended guidance for `dual-auth-rbac` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Three-Tier Panel Structure Context`
- `Architecture`
- `Database Schema Essentials`
- `Password Security`
- `JWT Architecture`
- `Session Management`
- `RBAC Permission Resolution`
- `Authentication Flows`
- `Multi-Tenant Isolation`
- `Security Checklist`
- `Middleware Pattern`
- `Environment Variables`
- Additional deep-dive sections continue in the reference file.
