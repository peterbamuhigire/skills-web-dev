# Skills Repository Overview

This repository is a working catalog of reusable AI-assistant skills and
supporting documentation. It combines implementation guidance, product strategy,
security patterns, finance doctrine, mobile development guidance, SDLC
documentation templates, and catalog maintenance tooling.

## What Is Here

| Area | Location | Notes |
| --- | --- | --- |
| Main skill catalog | `skills/` | Broad software, AI, SaaS, mobile, security, UX, and product skills. |
| Finance doctrine | `doctrine/skills/` | Canonical accounting, audit, reporting, IFRS, controls, and close guidance. |
| SDLC initialization | `00-meta-initialization/` | Entry-point project documentation workflow and examples. |
| Routing docs | `docs/skill-routing-index.md` | Human-readable consolidation and routing policy. |
| Alias data | `docs/skill-aliases.yml` | Machine-readable skill alias map. |
| Maintenance scripts | `scripts/` | Guardrail checks and setup helpers. |
| Long-form references | `book-extractions/`, `claude-guides/`, `blog-posts/` | Source material and companion writing. |

## How To Work In This Repo

1. Identify the relevant skill or routing entry.
2. Read the skill `SKILL.md` and only the references needed for the task.
3. Keep skill frontmatter concise and accurate.
4. Update routing docs when a parent skill absorbs or supersedes another skill.
5. Run the guardrail report before finishing catalog maintenance:

   ```powershell
   python -X utf8 scripts\skill_catalog_guardrails.py --report-only
   ```

## Current Catalog Policy

- Active roots are `skills/`, `doctrine/skills/`, and `00-meta-initialization/`.
- Target active catalog size is 150-170 skills.
- The guardrail hard cap is 200 active `SKILL.md` files.
- Finance doctrine is canonical in `doctrine/skills/`.
- Compatibility aliases under `skills/finance/` are temporary until absorbed or
  redirected.

## Related Docs

- [Project brief](PROJECT_BRIEF.md)
- [Tech stack](TECH_STACK.md)
- [Architecture](ARCHITECTURE.md)
- [Plans index](../plans/INDEX.md)
- [Next features](../plans/NEXT_FEATURES.md)
- [Agent guide](../../AGENTS.md)
