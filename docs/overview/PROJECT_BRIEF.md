# Project Brief

## Summary

This repository is a curated AI skills and documentation engine. It helps
coding agents and human operators select reusable workflows for software
engineering, AI systems, SaaS operations, finance-doctrine orchestration, mobile development,
security, UX, and SDLC documentation.

The current catalog includes a consolidated enterprise Java/JVM engineering
route and WWDC26-era Apple development guidance across iOS,
mobile operations, AI, App Intents/Siri/Spotlight, StoreKit, quality/release,
security, PWA/Safari, and companion design-system routing.

## Primary Users

| User | Need |
| --- | --- |
| Coding agents | Fast skill discovery, accurate routing, concise execution rules. |
| Developers | Reusable implementation guidance and quality gates. |
| Product and operations teams | Product, SaaS, documentation, and governance playbooks. |
| Finance implementers | Canonical accounting, controls, close, audit, and reporting doctrine. |

The shared control-plane registry describes twelve engines; the 2026-09-06
local Kaizen scope covers the eleven installed checkouts confirmed by the user.
See `docs/engine-control-plane.md` and the audit's portfolio progress record.

## Outcomes

- Reduce repeated prompt and documentation work.
- Keep domain rules close to execution guidance.
- Maintain a skill catalog that is small enough to route reliably, with routing
  precision measured (not assumed) and guarded in CI.
- Turn agent output into production-grade work a team can maintain: every
  meaningful change carries a Delivery Definition of Done pack (tests, release,
  rollback, runbook, maintenance notes).
- Preserve deep references without making every skill entrypoint heavy.
- Support Windows, Ubuntu, and Debian consumers with portable Markdown and
  Python tooling.
- Give downstream Python projects a repeatable path from multiple scripts or
  GUIs to a launcher, shared executable suite, portable archive, installer,
  signing boundary, CI build, and release evidence.

## Non-Goals

- This is not a deployable application.
- This repository does not expose an HTTP API.
- This repository does not own a database schema.
- This repository should not be treated as a package registry without an
  explicit release workflow.

## Current Risks

- The active skill count is 179, nine above the 150-170 soft target; future additions
  still need alias discipline. The CI guardrail (200 hard cap) and the collision
  detector keep this from becoming routing noise.
- Inactive aliases must stay documented in `docs/skill-aliases.yml`; the
  alias-integrity check now fails CI on a stale or unrouted alias, so this is
  caught automatically rather than by memory.
- New skills can shadow a neighbour's routing. Add a fixture to
  `scripts/routing_fixtures.yml` for any skill a sibling could steal traffic
  from, so the smoke test guards it.
- Apple beta-era APIs can change after WWDC26; keep code examples
  availability-gated and source-labeled until final release notes are reviewed.
