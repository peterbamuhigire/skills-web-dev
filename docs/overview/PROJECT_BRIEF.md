# Project Brief

## Summary

This repository is a curated AI skills and documentation engine. It helps
coding agents and human operators select reusable workflows for software
engineering, AI systems, SaaS operations, finance doctrine, mobile development,
security, UX, and SDLC documentation.

## Primary Users

| User | Need |
| --- | --- |
| Coding agents | Fast skill discovery, accurate routing, concise execution rules. |
| Developers | Reusable implementation guidance and quality gates. |
| Product and operations teams | Product, SaaS, documentation, and governance playbooks. |
| Finance implementers | Canonical accounting, controls, close, audit, and reporting doctrine. |

## Outcomes

- Reduce repeated prompt and documentation work.
- Keep domain rules close to execution guidance.
- Maintain a skill catalog that is small enough to route reliably.
- Preserve deep references without making every skill entrypoint heavy.
- Support Windows, Ubuntu, and Debian consumers with portable Markdown and
  Python tooling.

## Non-Goals

- This is not a deployable application.
- This repository does not expose an HTTP API.
- This repository does not own a database schema.
- This repository should not be treated as a package registry without an
  explicit release workflow.

## Current Risks

- The active skill count is above the configured cap.
- Several finance skills have duplicate frontmatter names between
  `doctrine/skills/` and `skills/finance/`.
- `doctrine` appears as a modified path in git and should be handled carefully
  before unrelated changes touch that area.
