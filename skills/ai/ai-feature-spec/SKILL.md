---
name: ai-feature-spec
description: Use when specifying one AI-powered feature end to end, including model choice, prompt and context contracts, output schema, fallbacks, human oversight, UX states, and evaluation.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Feature Specification

## Operating contract

## Inputs

| Input | Required | Purpose |
|---|---|---|
| Domain evidence | yes | named user problem, workflow context, data sensitivity, acceptance criteria, budget, latency target, and oversight need |

## Outputs

- Produce: feature blueprint, model and prompt contract, output schema, fallback states, oversight path, and test plan.

## Capability and permission boundaries

Default to read-only analysis. Read only scoped records; redact secrets and regulated data. Writes, execution, network calls, production configuration, customer communication, billing changes, and delegation require explicit authority and an identified owner. Never widen tenant, time-window, or system scope implicitly.

## Degraded mode

When required telemetry, evidence, execution, network access, or write authority is unavailable, return a partial result with each unassessed item labelled, preserve the safest existing state, and state the evidence or approval needed to continue. Never convert missing evidence into a pass.

## Decision rules

| Condition | Action |
|---|---|
| Scope, owner, or threshold is missing | Stop the affected decision and request it |
| Evidence is incomplete but read-only analysis is safe | Produce a qualified partial result and gap list |
| A mutation exceeds authority or tenant boundary | Block it and route for approval |
| Evidence meets the stated threshold | Issue the output with provenance and owner |

## Anti-Patterns

- Treating absent evidence as success. Fix: mark the check unassessed and name the missing source.
- Expanding one tenant or workflow to all tenants. Fix: enforce supplied scope at every query and action.
- Performing a production write during analysis. Fix: emit a reviewed change plan until authority is explicit.
- Reporting a metric without population, window, or source. Fix: attach all three.
- Hiding a failed threshold inside an average. Fix: report failure slices and the remediation owner.

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Design a single AI-powered feature end-to-end — model selection, prompt engineering, context window, output schema, fallback behaviour, human oversight, and UX integration. Invoke for each opportunity identified in ai-opportunity-canvas.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | AI feature spec | Markdown doc covering model, prompt, output schema, fallback, and unit-economics decisions | `docs/ai/feature-spec-assistant.md` |
| Correctness | AI feature evaluation report | Markdown doc covering pre-release evaluation against acceptance criteria | `docs/ai/feature-eval-assistant.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Purpose

Produce a complete, implementation-ready blueprint for one AI-powered feature. This is the specification artifact that drives both development and the AI Integration Section of the SRS/HLD.

**Invoke this skill:** Once per AI opportunity, after `ai-opportunity-canvas` has ranked it.

---

## Feature Blueprint Template

```
## AI Feature Blueprint: [Feature Name]

**Feature ID:** AI-[NNN]
**Module:** [Parent module]
**Pattern:** [From the 10 patterns in ai-opportunity-canvas]
**AI Module Tier:** Starter / Growth / Enterprise
**Status:** Draft / Approved

### 1. Business Goal
[One sentence: what user problem this solves and the measurable outcome]

### 2. Trigger
[What event or user action initiates the AI call]
- User-initiated: [button click / form submit / page load]
- System-initiated: [scheduled job / data change event]

### 3. Model Selection
[Selected model and rationale — see Model Selection Guide below]

### 4. Input Context
[Exactly what data is assembled and sent to the model]
- System prompt: [purpose and persona]
- Data injected: [table names, field names, row limits]
- Max input tokens: [number]

### 5. Output Schema
[Exact structure the model must return]
- Format: JSON / Markdown / Plain text
- Schema: [field names, types, constraints]
- Validation: [how output is checked before showing to user]

### 6. Prompt Design
[The system prompt text — production-ready]

### 7. Fallback Behaviour
[What the system does if the AI call fails, times out, or returns invalid output]

### 8. Human Oversight
[When a human must review before action is taken]

### 9. Token Estimate
[Input tokens per call, output tokens per call — feeds ai-cost-modeling]

### 10. UX Integration
[Where result appears, loading state, streaming vs batch, feedback mechanism]
```

---

## Problem-first and control addendum

Before selecting a model, state the user/system problem, compare a non-AI
alternative, and map human actors, system controls, model, inputs, outputs,
affected non-users, and failure consequences. For every action, specify preview,
uncertainty, correction, contest, undo or safe fallback, escalation, consent or
notice, and an audit event. Send current legal or platform claims to
`digital-research-engine` for verification.

## Model Selection Guide

Choose the cheapest model that reliably handles the task.

| Task Complexity | Recommended Model | Fallback |
|----------------|-------------------|---------|
| Summarisation, classification, short extraction | Codex Haiku 4.5 / Gemini 2.0 Flash / GPT-4o mini | DeepSeek V3 |
| Multi-step reasoning, structured JSON output, analysis | Codex Sonnet 4.6 / GPT-4o | Codex Haiku 4.5 |
| Complex document analysis, long context (> 50K tokens) | Codex Sonnet 4.6 (200K context) | Gemini 1.5 Pro |
| Image / document OCR + extraction | Codex Sonnet 4.6 / GPT-4o Vision | Gemini 2.0 Flash |
| Cost-critical, high volume (> 1,000 calls/day) | DeepSeek V3 / Gemini 2.0 Flash | GPT-4o mini |

**Rule:** Always start with the cheapest adequate model. Upgrade only when output quality is demonstrably insufficient.

**Provider abstraction:** Always code against a provider-agnostic interface so the model can be swapped without rewriting feature logic. See `ai-architecture-patterns`.

---

## Prompt Engineering Standards

### System Prompt Structure

```
You are [role] for [system name].
Your task: [one precise sentence].
Output format: [JSON schema / markdown structure / plain text].
Constraints:
- [constraint 1]
- [constraint 2]
Language: [English / Luganda / Swahili — match user locale]
```

### Rules

1. **Role-first** — Open with a clear role statement. It anchors model behaviour.
2. **One task per prompt** — Do not ask the model to summarise AND classify in one call.
3. **Explicit output format** — Always specify format. For JSON, embed the schema in the prompt.
4. **Inject only relevant data** — Do not send entire tables. Pre-filter in SQL before sending.
5. **Set a token budget** — Tell the model its output limit: "Reply in under 200 words."
6. **Language instruction** — Specify the output language explicitly for African deployments.
7. **No PII in prompt unless necessary** — See `ai-security` for PII scrubbing rules.

### Few-Shot Pattern (for classification tasks)

```
Examples:
Input: "Paid via MoMo on 15 March" → Category: "Mobile Money Payment"
Input: "Returned goods, credit note issued" → Category: "Credit Note"
Input: [user_input] → Category:
```

---

## Output Schema Design

For structured outputs, always use JSON with a validation step before displaying to users.

**Example — Predictive Alert:**
```json
{
  "alert_level": "high|medium|low",
  "summary": "string (max 100 chars)",
  "reason": "string (max 300 chars)",
  "recommended_action": "string (max 200 chars)",
  "confidence": "high|medium|low",
  "data_points_used": ["string"]
}
```

**Validation rule:** If the model returns an unparseable response or a field fails its constraint, log the failure, return the fallback, and flag for review. Never display raw model output directly.

---

## Fallback Behaviour Patterns

| Failure Mode | Fallback Action |
|--------------|----------------|
| API timeout (> 10s) | Show cached last result with timestamp; offer retry |
| Invalid JSON output | Log error, show "Analysis unavailable — try again" |
| Budget exceeded (gate blocked) | Show "AI module limit reached — contact admin" |
| Model returns refusal | Show neutral placeholder; do not expose model refusal text to end user |
| API provider outage | Queue the request, process when restored; notify user |

---

## Human Oversight Patterns

Apply oversight based on action severity:

| Decision Type | Oversight Level |
|--------------|----------------|
| Display only (summary, report) | None — show directly |
| Suggestion (recommend reorder) | Soft — user can accept/dismiss |
| Action with cost (send alert, flag account) | Hard — require explicit confirm |
| Irreversible action (delete, blacklist, approve loan) | Mandatory human approval gate |

---

## Token Estimation Worksheet

```
Input tokens  = system_prompt_tokens
              + injected_data_tokens
              + user_query_tokens

Output tokens = expected_response_tokens

Total per call = input + output

Calls per user per day = [estimate from use case]
Monthly tokens per user = total_per_call × calls/day × 30
```

Feed these numbers into `ai-cost-modeling` for cost and pricing calculations.

---

## Anti-Patterns

- Never send more data than the model needs — pre-filter in the application layer.
- Never display raw model output without validation and sanitisation.
- Never make irreversible actions AI-initiated without a human confirmation step.
- Never hardcode a specific model — use a configurable provider abstraction.
- Never skip the fallback — AI APIs have non-trivial failure rates.

---

**See also:**
- `ai-opportunity-canvas` — Source of AI features to spec
- `ai-cost-modeling` — Token cost and pricing from estimates here
- `ai-architecture-patterns` — Provider abstraction and gate implementation
- `ai-security` — PII rules and output sanitisation
- `ai-ux-patterns` — UX for loading, streaming, feedback
