# Source Patterns

This file transforms the supplied PDFs into reusable workflows and decision frameworks for Claude Code skills.

## Web Performance Engineering in the Age of AI

### Workflow: Performance-First Build Loop

1. Identify the top 3 user flows and mark the LCP, interaction, and stability moments inside each.
2. Set budgets before coding: HTML, JS, CSS, fonts, images, API latency, render time.
3. Build the flow with progressive delivery: server work first, then critical content, then enhancements.
4. Measure in lab and field conditions on realistic mobile hardware and unstable networks.
5. Remove waste in priority order: blocking resources, duplicate work, over-hydration, oversized assets, slow queries.
6. Re-test after every significant UX or AI integration change.

### Decision Framework

- If it helps first paint or first useful action, prioritize it.
- If it adds more CPU than user value, defer or remove it.
- If AI features increase bundle size or request cost, isolate them behind lazy boundaries and explicit budgets.
- If an optimization is invisible in field data, do not over-invest.

### Reusable Patterns

- Performance budgets as merge gates.
- Critical-path mapping per route or journey.
- Priority hints for hero assets and deferred loading for low-value code.
- AI feature isolation: streaming, caching, queueing, and cost-aware fallback.

## The AI Cybersecurity Handbook

### Workflow: Threat-Led Design

1. Enumerate assets: identities, data, models, prompts, logs, secrets, billing, admin actions.
2. Map adversaries: outsider, compromised user, malicious insider, third-party dependency, automated attacker.
3. List likely attacks by stage: recon, access, lateral movement, deception, abuse, persistence, exfiltration.
4. Add controls at each stage: rate limits, monitoring, least privilege, anomaly detection, approval gates, segmentation.
5. Instrument logs and alerts for high-risk paths before launch.
6. Rehearse incident response for credential loss, data leakage, webhook abuse, and account takeover.

### Decision Framework

- If a feature increases discovery, automation, or impersonation risk, require stronger verification and telemetry.
- If a model or automation can act on behalf of users, add human approval for destructive or financial actions.
- If explainability is weak, narrow authority and increase observability.

### Reusable Patterns

- Abuse-case-first threat model.
- Trust-boundary map with approval gates.
- Security telemetry matrix: auth, authz, admin, billing, data export, model/tool use.

## The Fundamentals of UX Writing

### Workflow: Microcopy Production

1. Name the user intent in plain language.
2. Write the shortest phrase that helps the user act correctly.
3. Add consequence or recovery when risk or ambiguity exists.
4. Check for consistency with product vocabulary.
5. Check for accessibility, localization growth, and screen-reader clarity.
6. Review empty, loading, success, and error states together, not in isolation.

### Decision Framework

- If text does not change the next user action, remove it.
- If a button label is generic, rewrite as verb plus object.
- If an error lacks a fix, it is incomplete.

### Reusable Patterns

- Verb-plus-object CTAs.
- Three-part errors: what happened, why, what to do next.
- Empty states that teach value and provide an action.

## Git Mastery Accelerated Crash Course

### Workflow: Safe Local Change Loop

1. Start with a clean understanding of the branch and working tree.
2. Make small coherent changes grouped by intent.
3. Stage selectively.
4. Write a commit message that records purpose, not mechanics.
5. Review your own diff before pushing.
6. Keep history readable enough for later recovery.

### Reusable Patterns

- Small commits with single intent.
- `.gitignore` hygiene.
- SSH-based authenticated remote workflow.
- Local history inspection before forceful operations.

## Git Fundamentals for New Developers

### Workflow: Team Collaboration Loop

1. Branch from an up-to-date base.
2. Pull frequently and integrate early to avoid conflict cliffs.
3. Keep feature branches short-lived.
4. Resolve conflicts with intent awareness, not marker deletion.
5. Push for review only after tests and diff review.
6. Merge with traceable history and release notes.

### Decision Framework

- If the change is not independently reviewable, split it.
- If the branch diverges too far, rebase or merge early.
- If recovery commands are required, prefer the least destructive option first.

### Reusable Patterns

- Trunk-friendly feature workflow.
- Conflict-resolution checklist.
- CI-linked review gate.
- Recovery before reset.

## Laws of UX

### Workflow: UX Heuristic Review

1. Identify the main decision, input, and feedback moments.
2. Check each moment against the relevant law: Hick, Fitts, Jakob, Tesler, Doherty, Peak-End, Zeigarnik.
3. Remove options, steps, or ambiguity that add cognitive cost without value.
4. Verify important actions are easy to notice and easy to hit.
5. Make endings, confirmations, and progress states clear and memorable.

### Reusable Patterns

- Choice reduction with recommended defaults.
- Large nearby primary actions.
- Convention-first navigation.
- Progress visibility for long flows.

## Software Design

### Workflow: Architecture Review

1. List responsibilities and invariants.
2. Group responsibilities into highly cohesive modules.
3. Reduce coupling across modules through explicit interfaces and contracts.
4. Compare at least two viable designs before implementation.
5. Record design decisions and why alternatives were rejected.
6. Evaluate reliability, maintainability, and testability before coding.

### Decision Framework

- If a module changes for multiple unrelated reasons, split it.
- If one change ripples through many modules, coupling is too high.
- If reliability depends on undocumented assumptions, the design is incomplete.

### Reusable Patterns

- Cohesion/coupling review.
- Alternative comparison before build.
- Recorded design rationale.
- Reliability-oriented design checks.

## Analyzing Websites

### Workflow: Website Analysis

1. Inspect the site as architecture: structure, navigation, hierarchy, linking.
2. Inspect it as discourse: tone, persuasion, credibility, semantic emphasis, audience fit.
3. Inspect it as a socio-technical system: ownership, workflows, moderation, personalization, data capture.
4. Inspect it as a communication device: calls to action, trust signals, conversion friction, narrative flow.
5. Turn observations into ranked issues and concrete design or content changes.

### Reusable Patterns

- Information architecture audit.
- Trust and credibility signal review.
- Link taxonomy and CTA hierarchy analysis.
- Semiotic review of wording, layout, and visual meaning.
