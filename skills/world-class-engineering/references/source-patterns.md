# Source Patterns

This file transforms the supplied books into reusable workflows and decision frameworks for Claude Code and Codex skills.

## Continuous Delivery

### Workflow: Deployment Pipeline Thinking

1. Treat every change as a release candidate from the moment it passes the commit stage.
2. Run a fast commit stage first: build, unit tests, static checks, packaging.
3. Promote the same artifact into automated acceptance, integration, and nonfunctional stages.
4. Use a final production decision gate only if risk, policy, or market timing requires it.
5. Design database and contract changes with overlapping-version safety.
6. Keep rollback, replay, and environment setup automated enough to rehearse.

### Reusable Patterns

- Commit stage plus downstream confidence stages.
- Build once, deploy many.
- Expand-contract schema evolution.
- Application-driver testing for acceptance-level workflows.
- Release candidate mindset instead of "works on my machine" mindset.

## Continuous Deployment

### Workflow: Inventory Reduction Through Automation

1. Reduce software inventory: long-lived branches, waiting QA queues, and unreleased code all count as waste.
2. Merge to trunk frequently and keep the branch strategy biased toward integration, not isolation.
3. Use automation to remove repetitive environment, test, and deployment work.
4. Prefer small releases and fast feedback over infrequent "big safe releases."
5. Use feature flags, dark launches, or controlled exposure to separate deploy from release when needed.
6. Treat pipeline friction as a flow problem to fix, not an excuse to batch more work.

### Reusable Patterns

- Trunk-based development.
- Small frequent releases.
- Inventory reduction as a design goal.
- Feature flags as release controls, not permanent architecture.
- Stop-the-line response to broken pipelines.

## The DevOps Handbook, Second Edition

### Workflow: Flow, Feedback, and Learning

1. Make the value stream visible from idea to production.
2. Optimize the bottleneck that most limits delivery speed or recovery.
3. Integrate operations concerns into daily engineering work.
4. Build deployment pipelines, telemetry, and low-risk releases as first-class system capabilities.
5. Use feedback from production, experimentation, and incidents to reshape the system.
6. Design team boundaries and architecture together so ownership and change flow stay aligned.

### Reusable Patterns

- Value-stream mapping.
- Deployment pipeline foundations.
- Fast and reliable automated testing.
- Telemetry for seeing and solving problems.
- Architecture and team design with Conway's Law in mind.

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

## Master Software Architecture

### Workflow: Architecture Evolution Loop

1. Understand the business domain before arguing about services or frameworks.
2. Identify bounded contexts, responsibilities, and integration pressure.
3. Choose deployment and release strategy together with architecture, not later.
4. Design testing, security, and operability as part of the architecture shape.
5. Start simple, then evolve only when load, team topology, or workflow complexity justify it.
6. Reassess architecture after major changes in scale, domain complexity, or release cadence.

### Reusable Patterns

- Context maps before service decomposition.
- Trunk-friendly releases with feature flags.
- Outbox and inbox patterns when asynchronous reliability matters.
- Architecture evolution by evidence, not anticipation.

## Fundamentals of Software Architecture

### Workflow: Tradeoff-Centered Architecture

1. Rank architectural characteristics for the specific system.
2. Compare options against those characteristics rather than abstract preference.
3. Record why the chosen option wins and what it makes harder.
4. Revisit the choice if business, scale, team, or compliance assumptions change.

### Decision Framework

- If you cannot name the tradeoff, you are not ready to decide.
- If a design choice improves one characteristic while silently harming another, document that cost explicitly.
- If simplicity and reversibility are available, prefer them.

### Reusable Patterns

- Architectural characteristics ranking.
- ADRs with explicit tradeoffs and consequences.
- Modularity review through cohesion and coupling.

## Software Development Pearls

### Workflow: Shared-Understanding Requirements Loop

1. Capture the user goal, business outcome, and usage context.
2. Turn ambiguous requirements into examples, edge cases, and constraints.
3. Review requirements as communication artifacts, not just scope lists.
4. Iterate at the highest useful level of abstraction before heavy implementation.
5. Make the product easy to use correctly and hard to use incorrectly.

### Reusable Patterns

- Usage-centric requirement framing.
- Scope boundaries with unresolved-question tracking.
- Design iteration before expensive build-out.

## The Effective Engineer

### Workflow: High-Leverage Execution

1. Prioritize the work with the biggest impact on users, revenue, risk, or team speed.
2. Increase iteration speed with faster tests, smaller changes, and low-friction tooling.
3. Validate ideas early with prototypes, experiments, or partial rollouts.
4. Measure the result and adjust based on evidence.
5. Reduce recurring operational burden with targeted automation.

### Reusable Patterns

- High-leverage prioritization.
- Validation-before-scale.
- Mechanics automation before decision automation.
- Idempotent recurring jobs.

## Modern Software Engineering

### Workflow: Throughput and Stability Balance

1. Treat software development as a product delivery system, not only a coding activity.
2. Measure both speed and stability.
3. Improve the bottleneck with the greatest impact on delivery quality.
4. Prefer evidence over process theater.
5. Keep the system adaptable as tools, teams, and markets change.

### Reusable Patterns

- Stability plus throughput scorecard.
- Delivery-system bottleneck analysis.
- Evidence-based process changes.

## Testing JavaScript Applications

### Workflow: Risk-Driven Test Portfolio

1. Decide what to prove, not just what to automate.
2. Put more tests at the fast layers and reserve slower layers for the behaviors only they can prove.
3. Use integration tests where module seams and real dependencies create risk.
4. Use end-to-end tests for a small number of high-value journeys.
5. Keep exploratory testing for ambiguity, UX issues, and scenarios automation misses.
6. Review test cost versus business risk instead of chasing raw coverage numbers.

### Reusable Patterns

- Testing pyramid with explicit exceptions.
- Acceptance versus end-to-end distinction.
- Exploratory testing for new or unclear behaviors.
- Test doubles only where they reduce noise without hiding risk.

## Observability Engineering

### Workflow: Diagnosis-First Telemetry

1. Start from the questions engineers and operators must answer during failure, latency, cost, and correctness problems.
2. Instrument events with enough dimensions to slice by actor, tenant, version, route, dependency, and release.
3. Use metrics for trend and alerting, traces for path analysis, logs for rich event context, and profiles when CPU or memory cost matters.
4. Manage cardinality deliberately instead of flattening away important debugging context.
5. Treat SLOs, cost, and performance telemetry as parts of one production feedback system.
6. For AI systems, instrument prompts, tool paths, retrieval stages, token usage, and quality eval outcomes.

### Reusable Patterns

- Wide structured events for debugging unknown failures.
- Release markers and deploy correlation.
- Cost-aware observability.
- AI and LLM telemetry with eval hooks.
- Profiling as part of production performance engineering.

## CI/CD Unleashed

### Workflow: Healthy Pipeline and Branching Discipline

1. Keep the pipeline as the only trusted path to production.
2. Run tests in an order that fails fast without removing critical confidence.
3. Use trunk-based development or similarly short-lived branches.
4. Use small, frequent releases to reduce blast radius.
5. Make broken builds an immediate team concern.
6. Match deployment strategy to risk, rollback speed, and monitoring strength.

### Reusable Patterns

- Blue-green, rolling, and canary rollout selection.
- Broken-build immediate response.
- Feature flags for release control.
- DORA metrics as delivery KPIs.

## Software Engineering at Google

### Workflow: Sustainable Engineering Organization

1. Make knowledge sharing normal through code review, docs, and visible work.
2. Treat readability and maintainability as velocity multipliers, not bureaucracy.
3. Build psychological safety so engineers surface problems early.
4. Scale quality through standards, review culture, automation, and shared ownership.
5. Reduce heroics by making knowledge and systems broadly accessible.

### Reusable Patterns

- Review culture focused on learning and maintainability.
- Knowledge-sharing over hidden work.
- Team-scale quality through standards and tooling.

## Become an Effective Software Engineering Manager

### Workflow: Team Operating Rhythm

1. Create clarity in priorities, roles, and decision ownership.
2. Use one-to-ones, delegation, and coaching to grow engineers rather than just direct them.
3. Balance stability and change so the team can learn without constant chaos.
4. Share information by default unless there is a real reason not to.
5. Build conditions for meaningful work, trust, and continuous improvement.

### Reusable Patterns

- Delegation by ownership.
- Coaching-first problem solving.
- Transparent management communication.

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
