---
name: ai-feature-spec
description: Design a single AI-powered feature end-to-end — model selection, prompt
  engineering, context window, output schema, fallback behaviour, human oversight,
  and UX integration. Invoke for each opportunity identified in ai-opportunity-canvas.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Feature Specification

<!-- dual-compat-start -->
## Use When

- Design a single AI-powered feature end-to-end — model selection, prompt engineering, context window, output schema, fallback behaviour, human oversight, and UX integration. Invoke for each opportunity identified in ai-opportunity-canvas.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-feature-spec` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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

## Model Selection Guide

Choose the cheapest model that reliably handles the task.

| Task Complexity | Recommended Model | Fallback |
|----------------|-------------------|---------|
| Summarisation, classification, short extraction | Claude Haiku 4.5 / Gemini 2.0 Flash / GPT-4o mini | DeepSeek V3 |
| Multi-step reasoning, structured JSON output, analysis | Claude Sonnet 4.6 / GPT-4o | Claude Haiku 4.5 |
| Complex document analysis, long context (> 50K tokens) | Claude Sonnet 4.6 (200K context) | Gemini 1.5 Pro |
| Image / document OCR + extraction | Claude Sonnet 4.6 / GPT-4o Vision | Gemini 2.0 Flash |
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
