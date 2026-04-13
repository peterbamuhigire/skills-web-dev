---
name: git-collaboration-workflow
description: Use when planning branch strategy, making commits, reviewing diffs, resolving
  conflicts, preparing pull requests, or shipping releases. Covers trunk-friendly
  collaboration, commit hygiene, conflict recovery, and CI-linked release discipline.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Git Collaboration Workflow

<!-- dual-compat-start -->
## Use When

- Use when planning branch strategy, making commits, reviewing diffs, resolving conflicts, preparing pull requests, or shipping releases. Covers trunk-friendly collaboration, commit hygiene, conflict recovery, and CI-linked release discipline.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `git-collaboration-workflow` or would be better handled by a more specific companion skill.
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
Use this skill to keep version control readable, reviewable, and recoverable. It is for disciplined delivery, not command memorization.

## Working Rules

- Keep `main` or the release branch deployable.
- Prefer small branches and small review units.
- Review your own diff before asking others to review it.
- Use recovery-first thinking before destructive commands.
- Treat commit history as shared operational documentation.

## Collaboration Workflow

### 1. Start Clean

Before coding:

- Confirm branch and upstream state.
- Inspect working tree changes.
- Separate unrelated work before starting.

### 2. Change in Reviewable Slices

Aim for commits that answer one question:

- What changed?
- Why now?
- What risk does it carry?

If one commit needs a long explanation to prove it is safe, split it.

### 3. Stage Intentionally

- Stage only files relevant to the current intent.
- Avoid "everything changed" commits unless it is truly mechanical and isolated.
- Re-read staged diffs before committing.

### 4. Write Useful Commits

Good commit messages state intent and scope:

- `feat: add invoice aging query for finance dashboard`
- `fix: prevent duplicate webhook processing on retry`
- `refactor: extract permission resolver from order service`

Avoid messages that only describe mechanics.

### 5. Integrate Early

- Rebase or merge from the base branch before divergence becomes expensive.
- Resolve conflicts with semantic understanding, not blind marker deletion.
- Re-run tests after integration, not only before it.

### 6. Review and Release

- PRs should explain impact, risk, and verification.
- Reviewers should focus on bugs, regressions, migration risk, and missing tests.
- Releases should include rollback awareness and post-deploy verification.
- Keep branch strategy coupled to CI quality and release safety, not personal preference.

## Decision Heuristics

Use rebase when:

- You want a clean linear feature history before merge.
- The branch is private or team conventions allow rewriting it.

Use merge when:

- Preserving integration history is useful.
- The branch is shared broadly and rewriting would create confusion.

Use revert before reset when:

- The bad change is already shared.
- You need an auditable undo in team history.

Require extra release notes when:

- schema or migration changes are present
- permissions, billing, or critical workflows changed
- rollout needs feature flags, canaries, or manual checks

## Conflict Resolution Checklist

- Identify which side changed behavior and why.
- Reconstruct the intended end state.
- Re-run tests around the conflicting area.
- Re-check generated files, lock files, schema changes, and config files.
- Confirm no logic was silently dropped during resolution.

## Branch and Release Standards

- Keep `main` releasable or one step from releasable.
- Pair risky changes with migration notes, verification notes, and rollback notes in the PR.
- Do not merge changes that require tribal knowledge to deploy safely.
- If CI is red for the branch strategy, the workflow is broken no matter how clean the history looks.

See [references/review-and-release.md](references/review-and-release.md) for PR and release checklists.

## Anti-Patterns

- Long-lived branches with hidden divergence.
- Mixed refactor-plus-feature-plus-formatting commits.
- Force pushes without team awareness on shared branches.
- Destructive recovery without first inspecting reflog-friendly options.
- PRs that ship without migration, rollback, or verification notes when needed.
- Treating Git workflow as separate from release engineering and CI health.

## References

- [references/review-and-release.md](references/review-and-release.md): Pull request, merge, and release checklists.
- [../world-class-engineering/references/source-patterns.md](../world-class-engineering/references/source-patterns.md): Git workflows derived from the supplied PDFs.
