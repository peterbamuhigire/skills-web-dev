[Back to Java Enterprise Development](../SKILL.md)

# AI in enterprise Java

Use this reference only for the Java integration boundary. Route opportunity,
model/provider choice, RAG, evaluation, agent architecture, safety, cost,
observability, security, and rollout to the engine's dedicated AI skills.

## Integration workflow

1. Start from an approved AI feature specification: user decision, acceptable
   error, prohibited action, data classes, human oversight, fallback, cost and
   latency budget, evaluation set, and rollout control.
2. Inspect the pinned Java framework and dependency graph. Verify every starter,
   annotation, client method, model identifier, vector-store adapter, tool API,
   and MCP integration against its exact official documentation.
3. Put model access behind an application port with explicit request, structured
   result, error, usage, timeout, cancellation, and policy metadata. Do not leak
   provider objects into domain logic.
4. Validate model output as untrusted input. Enforce schema, size, content,
   authorisation, tenant, tool allowlist, and business invariants before a side
   effect.
5. Bound context, retrieval, tools, retries, concurrency, queues, response size,
   streaming lifetime, and cost. Separate transient provider failure from safety
   refusal, invalid output, quota, and application-policy denial.
6. Instrument latency, errors, usage/cost dimensions, model/config/prompt/tool
   version, retrieval quality, safety decisions, and user outcome without
   logging sensitive prompts, credentials, personal data, or full documents.
7. Test deterministic application policy around the probabilistic component.
   Run task evaluations, adversarial cases, tenant-isolation tests, malformed
   structured outputs, prompt injection/tool abuse, provider outage, timeout,
   and fallback before controlled rollout.

## Spring AI and alternative clients

Spring AI may provide model, embedding, vector-store, tool-calling, structured-
output, MCP, and observation integrations for a compatible Spring generation.
Use its BOM/starter alignment and current API documentation; rapid API change
makes remembered examples unsafe. A provider SDK or framework-neutral client
may be simpler when the application uses one narrow capability or must avoid
framework coupling. Record an ADR based on portability, feature coverage,
version stability, observability, testing, and team ownership.

## Transaction and tool boundaries

- Never hold a database transaction or lock open across an uncontrolled model
  call. Gather authorised context, commit/read snapshot as needed, call the
  model, then revalidate state/version before any write.
- Give tools typed, narrow inputs and service-side authorisation. The model does
  not decide tenant, actor, privilege, monetary limit, or irreversible approval.
- Require idempotency and approval for consequential actions. Persist an
  attempt/outcome ledger that distinguishes proposed, approved, executed,
  failed, compensated, and abandoned work.
- Treat retrieved text, web content, documents, MCP results, and tool outputs as
  data that may contain instructions; preserve trust boundaries and provenance.
- Stream responses with cancellation, disconnect handling, bounded buffering,
  partial-result policy, and no claim that a partial stream completed.

## Data and privacy

Classify prompts, retrieved chunks, embeddings, outputs, traces, and evaluation
datasets. Apply tenant isolation, access control, minimisation, retention,
deletion/export, regional/provider constraints, encryption, and audit rules
from the owning privacy/security skills. Do not invent jurisdictional rules.
Vector deletion and model-provider retention are separate controls and require
provider and datastore evidence.

## Evaluation evidence

| Layer | Evidence |
|---|---|
| Java boundary | Compilation, client contract, timeout/cancellation, parsing and error mapping |
| Policy | Auth, tenant, tool allowlist, approval, idempotency and side-effect tests |
| AI quality | Versioned task set, rubric, baseline, failure taxonomy and reviewer agreement |
| Retrieval | Source permissions/provenance, relevance/grounding measures and stale-data tests |
| Operations | Latency/error/cost/safety telemetry, provider outage/fallback and rollback drill |

If model access or evaluation execution is unavailable, do not claim feature
quality. Mark it `NOT ASSESSED` while completing deterministic Java tests.

## AI-generated Java gate

- Read package/module boundaries, build files, toolchain, dependency management,
  framework configuration, persistence and tests before editing.
- Verify coordinates and APIs against the pinned version; invented annotations,
  configuration keys, model names, and client methods are blockers.
- Keep the patch small. Compile, run relevant tests/analysis and a realistic
  failure smoke; inspect output rather than reporting commands alone.
- Avoid speculative interfaces, factories, generic wrappers, reflection, and
  new dependencies. Preserve local style and architecture.
- Never fabricate build, test, evaluation, benchmark, cost, or safety results.

## Anti-patterns

- A controller calls a model and executes its text as a command. Parse into a
  typed proposal, authorise and validate server-side, then require approval.
- Model calls inside `@Transactional` methods. Split external latency from the
  short consistency boundary and re-check state before commit.
- Logging prompts and outputs for convenience. Apply data classification,
  redaction/minimisation, access and retention first.
- RAG called grounded because citations are displayed. Verify retrieval
  permissions, source support, locator integrity, and answer evaluation.
- Passing an AI unit test with a single live model response. Use controlled
  fakes for Java policy plus versioned evaluation against the actual model.

