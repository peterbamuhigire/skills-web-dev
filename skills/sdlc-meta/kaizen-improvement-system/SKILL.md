---
name: kaizen-improvement-system
description: Use when auditing or improving this engineering engine or a product it produces. Coordinates evidence-backed baselines, small experiments, standardisation, and re-audits without replacing domain skills.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Kaizen Improvement System

Use this skill to turn observed defects, incidents, feedback, source changes,
or audit gaps into small, reversible, evidence-backed improvements. It keeps
domain judgement with the owning engine and makes learning discoverable.

<!-- dual-compat-start -->
## Use When

- Auditing or grading the engineering catalogue or a product made with it.
- Turning defects, incidents, user feedback, or new evidence into a tested improvement.
- Planning a major iteration, quarterly engine review, or post-release re-audit.

## Do Not Use When

- A single-skill safety review is the only task; use `skill-safety-audit`.
- A current external claim is needed before source evaluation and verification.
- The proposed change is cosmetic and has no measurable effect on routing, quality, safety, or delivery.

## Required Inputs

- Engine or product path, intended audience, output types, owner, and constraints.
- Current routes, references, tests, user or product evidence, and known failure modes.
- Baseline scoring method, improvement target, acceptance evidence, rollback condition, and re-audit date.

## Prerequisites

- Read `docs/continuous-improvement/kaizen-adoption-2026-08.md`.
- For portfolio or current-standards claims, use the Digital Research engine's source-evaluation and source-verification routes.

## Workflow

1. **Observe.** Inspect the real route, output, users, constraints, evidence, and failure mode.
2. **Baseline.** Inventory applicable dimensions and score them with named evidence. Keep raw scores, blockers, uncertainty, and `NOT ASSESSED` items visible. Publish the repository policy cap of `min(raw_score, 65)` for permanent audits.
3. **Select.** Choose the smallest high-leverage root cause. Prefer repeated defects, user harm, safety issues, missing proof, and routing failures over added prose.
4. **Experiment.** Name the exact skill, reference, fixture, validator, or gate; hypothesis; owner; measure; risk; rollback; stop condition; and re-audit date.
5. **Check.** Re-run relevant validators, tests, source checks, user or product checks, and independent review. Preserve negative evidence.
6. **Standardise.** Promote a successful result into the owning skill, reference, template, fixture, router, or release gate. Do not promote a one-off observation.
7. **Teach and re-measure.** Update discoverability and handoffs, re-score the changed dimensions, and leave the next improvement visible.

## Core content

For a product, assess the applicable combination of requirements, architecture
or document correctness, security and privacy, accessibility, reliability,
performance, user value, deployment or handoff, rollback, and evidence quality.
For an engine, assess doctrine, taxonomy and routing, skill depth, applied
proof, standards currency, output readiness, hygiene, safety, and integrity.

## Quality Standards

- Scores cite concrete evidence and a one-line deficiency statement.
- A target of 95/100 is an improvement target, not an achievement claim.
- Do not award 70+ without extraordinary, specific proof or claim production readiness without executable or rendered evidence.
- Structural, behavioural, render, system, and production evidence are labelled separately.
- Missing execution, source, approval, or artefact evidence is `NOT ASSESSED`.
- A safety, legal, financial, privacy, security, or release blocker remains a blocker regardless of score.
- Lessons are stored only when repeatable, generalisable, significant, actionable, and likely to prevent recurrence.

## Anti-Patterns

- Adding a skill without a demonstrated routing or ownership gap. Fix: inventory and test the collision first.
- Awarding a high score because headings or checkboxes exist. Fix: require outcome-level evidence.
- Treating a green unit or structural test as product proof. Fix: add the smallest relevant behavioural, failure, render, or handoff check.
- Closing an action because prose changed. Fix: close only when named acceptance evidence exists and a fresh agent can find the result.
- Hiding an unavailable check inside an overall score. Fix: mark it `NOT ASSESSED` with an owner and date.
- Keeping every retrospective note forever. Fix: promote durable learning and remove redundant narrative.

## Outputs

| Artifact | Consumed by | Template |
|---|---|---|
| Capped scorecard and evidence register | Maintainer and reviewer | Kaizen adoption plan and local report |
| Improvement action record | Owner and implementer | Gap, root cause, change, hypothesis, measure, risk, rollback, evidence |
| Standardisation record | Future agents and router | Skill, reference, fixture, validator, or gate change |
| Re-audit handoff | Next reviewer | Date, owner, remaining gaps, and required checks |

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Correctness | Baseline and re-score | Markdown table | Raw dimensions, cap, blockers, and evidence |
| Security | Safety and integrity review | Markdown | Permission, provenance, and harmful-output findings |
| Operability | Rollback and re-audit handoff | Markdown | Owner, stop condition, recovery, and next date |
| Release evidence | Validator and test record | Command output or Markdown | Positive, negative, and unavailable checks |

## Read next

- `skill-engine-audit` for the engine rubric and evidence matrix.
- `skill-safety-audit` for changed or imported skill safety review.
- `advanced-testing-strategy` for risk-scaled validation.
- `world-class-engineering` for delivery gates and operational handoff.

## Mandatory Digital Research currentness gate

Every Kaizen cycle must begin with `digital-research-engine` source evaluation
and source verification. Record scope, dates, freshness class, support status,
uncertainty, and review date for current standards, APIs, frameworks, packages,
security, platform, and lifecycle claims; quarantine unsupported claims as
`NOT_ASSESSED`. Apply the currentness gate at
`C:/wamp64/www/digital-research-engine/docs/continuous-improvement/kaizen-currentness-gate.md`.

## References

- `docs/continuous-improvement/kaizen-adoption-2026-08.md` - local adoption plan.
- `C:/wamp64/www/digital-research-engine/docs/continuous-improvement/portfolio-kaizen-standard-2026-08.md` - cross-engine standard.
- `skills/sdlc-meta/skill-engine-audit/` - audit dimensions, scoring, and report structure.
- `skills/sdlc-meta/skill-safety-audit/` - safety and source-ingestion gate.
<!-- dual-compat-end -->

## Inputs

| Artefact | Produced by | Required? | Why |
|---|---|---|---|
| Engine or product path and output types | Router or task owner | yes | Fixes the audit boundary |
| Current evidence and failure history | Validators, tests, users, or operators | yes | Prevents opinion-only scoring |
| Target and constraints | Task owner | yes | Defines the experiment and rollback |

## Capability contract

Read and search are required. Execution is preferred for validators and tests;
editing requires an authorised improvement scope. Without execution, report the
exact checks as `NOT ASSESSED`. Network research is optional and must use
source-disciplined routes.

## Degraded mode

If a validator, source, user result, render, system environment, or independent
review is unavailable, keep the gap visible and state its consequence. Return a
conditional plan or verdict; never convert unavailable evidence into a pass.

## Decision rules

| Condition | Action | Failure avoided |
|---|---|---|
| A repeated defect has a clear owning skill or gate | Patch that source of truth and add a focused regression check | Symptom-only fixes and recurrence |
| The proposed change adds only prose or a duplicate route | Do not change the catalogue; record the gap or route to the existing owner | Kaizen bloat and routing noise |
| The result changes a cross-engine handoff | Require source owner, receiving owner, artefacts, uncertainty contract, and fallback | Silent ownership drift |
| A material outcome, render, system, or production check cannot run | Mark it `NOT ASSESSED` and retain the blocker | False readiness |
| The experiment passes its acceptance evidence | Standardise the result and schedule re-measurement | Learning lost in a one-off patch |

The book-wave operating contract is [book-driven system decision and agent orchestration](../references/book-driven-system-decision-and-agent-orchestration.md). Current technology and security claims must pass Digital Research verification.

The 2026-09-02 cross-engine study is [Book-driven Kaizen Wave 3](references/book-driven-kaizen-wave-3-2026-09-02.md); use it for currentness-gated contracts, testing, Git recovery, secure input handling, protocol semantics, and agent evaluation.
