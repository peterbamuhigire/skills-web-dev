---
name: vibe-security-skill
description: This skill helps Claude write secure web applications. Use when working
  on any web application to ensure security best practices are followed.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Secure Coding Guide for Web Applications

<!-- dual-compat-start -->
## Use When

- This skill helps Claude write secure web applications. Use when working on any web application to ensure security best practices are followed.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `vibe-security-skill` or would be better handled by a more specific companion skill.
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
## Overview

This skill provides comprehensive secure coding practices for web applications, mapped to OWASP Top 10 2025. As an AI assistant, your role is to approach code from a **bug hunter's perspective** and make applications **as secure as possible** without breaking functionality.

**Key Principles:**
- Defense in depth: Never rely on a single security control
- Fail securely: When something fails, fail closed (deny access)
- Least privilege: Grant minimum permissions necessary
- Input validation: Never trust user input, validate everything server-side
- Output encoding: Encode data appropriately for the context it's rendered in

**Deployment Context:** Apps deploy across Windows (dev), Ubuntu (staging), and Debian (production). Security must work on all platforms:
- File permissions differ: test upload dirs and temp paths on Linux
- Case-sensitive filesystems on Linux can expose hidden files if not careful
- Use `utf8mb4_unicode_ci` collation to prevent charset-based injection edge cases
- Never hardcode Windows paths; use `DIRECTORY_SEPARATOR` or `/`

**OWASP Top 10 2025:** A01 Broken Access Control • A02 Security Misconfiguration • A03 Supply Chain • A04 Cryptographic Failures • A05 Injection • A06 Insecure Design • A07 Authentication Failures • A08 Data Integrity Failures • A09 Logging Failures • A10 Exception Handling

📖 **See `references/owasp-mapping.md` for complete vulnerability → OWASP mapping**

---

## Additional Guidance

Extended guidance for `vibe-security-skill` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Critical Real-World Vulnerabilities (AI Code Generation Blind Spots)`
- `OWASP Top 10 2025 - Quick Reference`
- `Quick Security Checklists`
- `Security Headers Reference`
- `General Security Principles`
- `Additional Resources`
