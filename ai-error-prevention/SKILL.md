---
name: ai-error-prevention
description: Error prevention strategies for AI-assisted development. Use when working
  with Claude to minimize hallucinations, incomplete solutions, and wasted tokens.
  Enforces "trust but verify" workflow.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# AI Error Prevention in Software Development

<!-- dual-compat-start -->
## Use When

- Error prevention strategies for AI-assisted development. Use when working with Claude to minimize hallucinations, incomplete solutions, and wasted tokens. Enforces "trust but verify" workflow.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-error-prevention` or would be better handled by a more specific companion skill.
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

This skill teaches you to **prevent errors BEFORE they happen** when working with Claude to generate code. It focuses on minimizing wasted tokens, catching Claude's mistakes early, and ensuring production-ready output.

**Documentation Structure (Tier 2 Deep Dives):**
- 📖 **[prevention-strategies.md](references/prevention-strategies.md)** - The 7 prevention strategies with detailed examples
- 📖 **[failure-modes.md](references/failure-modes.md)** - Common Claude failures and how to prevent them
- 📖 **[app-specific-prevention.md](references/app-specific-prevention.md)** - Prevention for MADUUKA, MEDIC8, BRIGHTSOMA, DDA

---

## When to Use This Skill

**Always use when:**
- Working with Claude to generate code
- Building software with AI assistance
- Want to minimize wasted tokens on wrong solutions
- Need to catch Claude's mistakes early
- Developing production-ready code with AI

**This skill prevents errors BEFORE they happen.**

---

## Additional Guidance

Extended guidance for `ai-error-prevention` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `The Core Problem`
- `The 7 Prevention Strategies (Quick Reference)`
- `Common Claude Failure Modes (Summary)`
- `AI Development Error Prevention Framework`
- `App-Specific Prevention (Summary)`
- `The Golden Rule`
- `Acceptance Checklist`
- `Token Waste Prevention`
- `Integration with Other Skills`
- `Summary`
