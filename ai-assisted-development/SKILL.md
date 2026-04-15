---
name: ai-assisted-development
description: Orchestrate AI agents (Claude Code and Codex and Codex and Codex and
  Codex and Codex and Codex and Codex and Codex and Codex and Codex and Codex and
  Codex and Codex and Codex, sub-agents, etc.) for software development workflows.
  Use when coordinating multiple AI assistants or planning AI-driven development processes.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# AI-Assisted Development Orchestration

<!-- dual-compat-start -->
## Use When

- Orchestrate AI agents (Claude Code and Codex and Codex and Codex and Codex and Codex and Codex and Codex and Codex and Codex and Codex and Codex and Codex and Codex and Codex, sub-agents, etc.) for software development workflows. Use when coordinating multiple AI assistants or planning AI-driven development processes.
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

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Overview

Learn to **orchestrate multiple AI agents** (like Claude Code, custom sub-agents, or specialized AI tools) to work together effectively in software development.

This skill bridges **prompting patterns** + **orchestration** + **sub-agent coordination** for real-world AI-assisted development.

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
