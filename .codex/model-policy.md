## Codex model and delegation policy

Peter's rule, effective 2026-09-07. Apply only in Codex. Claude and other
consumers retain their own model selection and all domain-engine capabilities.

- Root/orchestrator and final reviewer: `gpt-6-astra`.
- Execution subagents (default, worker, explorer, tester and researcher):
  default and explicitly pinned to `gpt-5.6-luna`, with medium reasoning.
- Delegate useful, bounded execution work to Luna. Astra owns scope,
  architecture, decomposition, integration, conflict resolution and final
  acceptance. A worker's self-approval is not an independent review.
- Every execution spawn must explicitly select `gpt-5.6-luna`; reviewer-only
  spawns must explicitly select `gpt-6-astra`. On hosts that prohibit model
  overrides with full-history forks, use a bounded-context or no-history fork
  with a sufficient task brief. Preserve the pin through nested execution.
- Give each worker its outcome, context, exact scope, file ownership,
  constraints, acceptance checks and evidence handoff. Use parallel writers
  only for independent ownership. Keep trivial tasks with the root.
- On worker failure, record it, inspect the cause, narrow or retry the task,
  and return unresolved decisions to Astra. Never silently substitute another
  execution model or claim delegation occurred without an actual spawn.
- Before final delivery, Astra reviews the real diff and relevant tests,
  integrates material findings, resolves conflicts and waits for required
  agents. Missing tests, sources or reviewers remain `NOT_ASSESSED`.
- Every Kaizen operation MUST check current official model releases and the
  active runtime/account model catalogue before retaining or proposing changes
  to the model policy. Record dated source URLs, model IDs, availability,
  task-fit evidence, cost/latency/quality considerations, uncertainties and a
  retain/change decision. Newer does not automatically mean better. Use the
  Digital Research currentness gate; do not infer latest status from memory.
- These pins remain until Peter authorises a verified replacement. A new
  release triggers evaluation, not a silent model switch. If current sources
  or model selection are unavailable, report the limitation and leave the
  model evaluation `NOT_ASSESSED`; do not weaken the engine's other gates.
- Configuration applies to newly started sessions; do not claim a running
  root changed models because a file was edited. Report any session override
  or unavailable pin. This is a configuration and agent-instruction policy,
  not an administrative restriction on the user's model controls.
