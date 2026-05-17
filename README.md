# Skills Repository

This repository is a curated skills catalog for AI-assisted software delivery,
product work, documentation, security, finance doctrine, mobile development,
and SaaS engineering.

The root README is intentionally short. The canonical project overview lives in
[`docs/overview/README.md`](docs/overview/README.md).

## Quick Start

1. Browse active skills in [`skills/`](skills/), [`doctrine/skills/`](doctrine/skills/),
   and [`00-meta-initialization/`](00-meta-initialization/).
2. Use [`docs/skill-routing-index.md`](docs/skill-routing-index.md) to choose the
   retained parent skill when a narrow or legacy skill has been consolidated.
3. Use [`docs/skill-aliases.yml`](docs/skill-aliases.yml) for machine-readable
   alias routing.
4. Run the catalog guardrail report before large catalog changes:

   ```powershell
   python -X utf8 scripts\skill_catalog_guardrails.py --report-only
   ```

## Key Docs

| Document | Purpose |
| --- | --- |
| [`docs/overview/PROJECT_BRIEF.md`](docs/overview/PROJECT_BRIEF.md) | One-page project brief. |
| [`docs/overview/TECH_STACK.md`](docs/overview/TECH_STACK.md) | Tooling, runtime assumptions, and platform notes. |
| [`docs/overview/ARCHITECTURE.md`](docs/overview/ARCHITECTURE.md) | Repository structure and ownership boundaries. |
| [`docs/plans/INDEX.md`](docs/plans/INDEX.md) | Planning document index. |
| [`docs/plans/NEXT_FEATURES.md`](docs/plans/NEXT_FEATURES.md) | Current priorities and next work. |
| [`AGENTS.md`](AGENTS.md) | Working rules for Codex and other coding agents. |

## Repository Shape

| Path | Role |
| --- | --- |
| `skills/` | Main active skill catalog. |
| `doctrine/skills/` | Canonical finance and accounting doctrine skills. |
| `00-meta-initialization/` | Entry-point SDLC documentation initialization skills and examples. |
| `docs/` | Analysis, routing, planning, operations, and overview docs. |
| `scripts/` | Repository maintenance scripts. |
| `claude-guides/` | Claude-specific guidance and skill authoring references. |
| `book-extractions/` | Curated notes and extracted source material. |
| `blog-posts/` | Draft content and educational material. |

## Current Known State

The catalog currently exceeds the active skill target and has known duplicate
finance frontmatter names between `doctrine/skills/` and `skills/finance/`.
That is tracked in [`docs/skill-routing-index.md`](docs/skill-routing-index.md)
and should be handled through consolidation or alias routing, not by deleting
directories casually.

There is no application runtime, HTTP API, database schema, or package manager
manifest at the repository root. This is primarily a Markdown, YAML, and Python
maintenance repository.
