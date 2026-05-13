---
name: sdlc-documentation
description: Use when producing, reviewing, or consolidating SDLC documentation across planning, requirements, design, testing, deployment, user rollout, post-deployment, and maintenance phases. Load absorbed SDLC phase references as needed.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SDLC Documentation
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

Use this parent skill as the active SDLC documentation entrypoint. Keep the phase-specific details in references and load only the phase being authored or reviewed.

<!-- dual-compat-start -->
## Use When

- Creating or reviewing SDLC document sets, delivery evidence, traceability, phase gates, and lifecycle handoffs.
- Consolidating planning, design, testing, deployment, user rollout, post-deployment, and maintenance documents.
- Aligning project documentation with implementation, validation, release, and support obligations.

## Do Not Use When

- The task is unrelated to this parent skill or is better handled by a narrower active parent named in the workflow.
- The request only needs a trivial answer and no reference module needs to be loaded.

## Required Inputs

- Gather the concrete system, repository, environment, constraints, and deliverable before loading references.
- Identify which absorbed reference file is needed; do not load every migrated reference by default.
## Workflow

1. Load `world-class-engineering` for baseline delivery quality.
2. Load the needed phase reference:
   - `references/sdlc-planning.md` for project planning and initiation.
   - `references/sdlc-design.md` for solution and technical design documents.
   - `references/sdlc-testing.md` for test planning, evidence, and acceptance gates.
   - `references/sdlc-user-deploy.md` for user rollout and adoption documents.
   - `references/sdlc-post-deployment.md` for go-live review and stabilisation evidence.
   - `references/sdlc-maintenance.md` for support, maintenance, and continuous improvement.
3. Pair with `project-requirements`, `advanced-testing-strategy`, `deployment-release-engineering`, or `implementation-status-auditor` when the task needs those outputs.

## Quality Standards

- Every document must be tied to a decision, acceptance criterion, release gate, or operating obligation.
- Preserve traceability from requirement to design, implementation, test evidence, release, and support.
- Avoid generic SDLC text that cannot guide an implementation or audit decision.

## Anti-Patterns

- Treating absorbed reference files as active skills or separate routing entrypoints.
- Loading every migrated child reference instead of the one that matches the task.
- Producing generic advice without constraints, evidence, or next verification steps.
## Outputs

- SDLC document, review findings, traceability notes, phase gate checklist, or handoff package.

## References

- Load only the eferences/<old-skill>.md files named in the workflow when their depth is required.
<!-- dual-compat-end -->
