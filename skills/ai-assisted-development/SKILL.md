---
name: ai-assisted-development
description: Orchestrate AI coding agents, human reviewers, CI, and delivery workflows
  for professional software work. Use when coordinating AI-assisted planning,
  implementation, code review, modernization, documentation, or multi-agent development.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# AI-Assisted Development Orchestration
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Orchestrate AI coding agents, human reviewers, CI, and delivery workflows for professional software work. Use when coordinating AI-assisted planning, implementation, code review, modernization, documentation, or multi-agent development.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-assisted-development` or would be better handled by a more specific companion skill.
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
| Release evidence | AI agent orchestration record | Markdown doc capturing agent assignments, hand-offs, and review checkpoints across the project | `docs/ai/agent-orchestration-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Overview

Learn to **orchestrate multiple AI agents** (like Claude Code, custom sub-agents, or specialized AI tools) to work together effectively in software development.

This skill bridges **prompting patterns** + **orchestration** + **sub-agent coordination** for real-world AI-assisted development.

## Operating Doctrine

- Treat AI as a force multiplier inside a disciplined engineering system, not as a replacement for requirements, design, review, tests, security, or ownership.
- Start every AI-assisted task with a concrete outcome, repo constraints, acceptance criteria, and verification command. Do not ask an agent to "improve" broad surfaces without a definition of done.
- Keep humans accountable for architecture, irreversible data changes, production release, security exceptions, licensing/IP decisions, and client commitments.
- Prefer small, reviewable AI work packets: one responsibility, one bounded write scope, one expected evidence artifact.
- Require codebase grounding before edits. The agent must inspect current patterns, interfaces, tests, and failure modes before proposing or changing implementation.

## AI Development Workflow

1. **Frame**: State user value, business value, technical objective, constraints, and acceptance tests.
2. **Ground**: Read the smallest set of files/docs needed to understand existing behavior.
3. **Plan**: Split work by ownership boundaries. Identify what can be delegated and what must stay on the critical path.
4. **Implement**: Make narrow changes that preserve local conventions. Avoid broad rewrites unless requested.
5. **Verify**: Run focused tests, linters, type checks, migrations, or manual checks that match the blast radius.
6. **Review**: Inspect diff for hallucinated APIs, over-broad abstractions, hidden state changes, secrets, data leaks, and licensing risks.
7. **Record**: Capture changed files, commands run, residual risks, and follow-up work.

## Agent Assignment Rules

- Use explorers for bounded codebase questions with clear expected outputs.
- Use workers for bounded implementation with disjoint file ownership. Tell workers they are not alone in the codebase and must not revert others' edits.
- Do not delegate the immediate blocking task if the main workflow cannot proceed until it returns.
- Never let two agents write the same files unless one is explicitly reviewing the other's patch.
- For generated code, require the same quality bar as human code: tests, readable names, explicit error handling, and no invented dependencies.

## AI Coding Risk Controls

| Risk | Control |
|---|---|
| Hallucinated APIs | Compile/typecheck and inspect imports, method names, schemas, and SDK versions |
| Plausible but wrong logic | Add examples, regression tests, and domain-specific fixtures |
| Security regression | Run threat review for auth, tenancy, file IO, network calls, secrets, and prompt injection |
| IP/license exposure | Avoid copying unknown code; check dependency licenses before adding packages |
| Context leakage | Keep secrets, credentials, client PII, and proprietary data out of prompts unless explicitly approved |
| Over-automation | Require human approval for production deploys, destructive changes, payments, emails, and client-facing commitments |

## Evidence Required

- For code changes: diff summary, tests/checks run, and known gaps.
- For architecture or plans: decision record, alternatives considered, evaluation criteria, and economic rationale.
- For modernization: before/after behavior, migration steps, rollback plan, and compatibility notes.

**What you'll learn:**
- The 5 orchestration strategies for AI development
- AI-specific coordination patterns (Agent Handoff, Fan-Out/Fan-In, Human-in-the-Loop)
- Real-world examples (MADUUKA, BRIGHTSOMA apps)

**Documentation Structure (Tier 2 Deep Dives):**
- 📖 **[orchestration-strategies.md](references/orchestration-strategies.md)** - The 5 core strategies with detailed examples
- 📖 **[ai-patterns.md](references/ai-patterns.md)** - AI-specific orchestration patterns
- 📖 **[practical-examples.md](references/practical-examples.md)** - Real MADUUKA and BRIGHTSOMA projects

---

## Additional Guidance

Extended guidance for `ai-assisted-development` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `When to Use This Skill`
- `Core Concepts (Quick Reference)`
- `The 5 Orchestration Strategies (Summary)`
- `The 3 AI Orchestration Patterns (Summary)`
- `Quick Reference: When to Use Which`
- `Real-World Examples (Summary)`
- `Practical Workflow: How to Apply This Skill`
- `Best Practices`
- `Integration with Other Skills`
- `Summary`
