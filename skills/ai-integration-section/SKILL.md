---
name: ai-integration-section
description: Generate a complete "AI Integration" section for any SRS, PRD, HLD, LLD,
  or design document. Covers AI opportunities, gate/billing design, cost model, architecture
  pattern, UX approach, and security posture for the module being documented. Invoke...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Integration Section
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Generate a complete "AI Integration" section for any SRS, PRD, HLD, LLD, or design document. Covers AI opportunities, gate/billing design, cost model, architecture pattern, UX approach, and security posture for the module being documented. Invoke...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-integration-section` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | AI Integration section of the design document | Markdown insertion covering opportunities, gates, and risks for the host SRS / PRD / HLD / LLD | `docs/design/ai-integration-section.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Purpose

Every significant document in an AI-enabled project must include an **AI Integration** section that answers:
1. **Why** — what business problem AI solves in this module
2. **What** — which specific AI features are included
3. **How** — architecture, gating, metering, security
4. **Cost** — token economics and pricing impact

This skill generates that section, ready to embed in the parent document.

---

## When to Invoke

Invoke this skill after generating any of:
- SRS Section 3.x (Functional Requirements for a module)
- PRD Feature Section
- HLD Module Description
- LLD Component Design
- API Specification for AI endpoints
- Any design document describing a module that handles user data

**Skip if** the module has no data the AI could use and no user decisions the AI could support.

---

## Discovery Checklist (Run First)

Before writing the section, answer these questions about the module:

1. What decisions does a user make in this module daily?
2. What data accumulates in this module over time?
3. What manual work here is repetitive but requires judgement?
4. What early warnings would save the user money or time?
5. Can AI reduce time-to-insight from hours to seconds for any task here?

If 2 or more answers suggest AI value, proceed. Otherwise note "No AI integration identified for this module."

---

## AI Integration Section Template

Insert this section into the parent document after the module's core requirements.

---

```markdown
## AI Integration — [Module Name]

### AI Opportunity Assessment

| ID | Opportunity | Pattern | Priority | AI Tier Required |
|----|------------|---------|----------|-----------------|
| AI-[NNN] | [description] | [pattern from ai-opportunity-canvas] | High/Med/Low | Starter/Growth/Enterprise |

*Full AI Opportunity Register: see `projects/[ProjectName]/_context/ai-opportunities.md`.*

### AI Features Specified

For each opportunity marked High or Medium priority:

#### [Feature Name] (AI-[NNN])

**Business Goal:** [One sentence — what user problem this solves]

**Trigger:** [User action or system event that initiates the AI call]

**Model:** [Model name] — selected for [cost/capability reason]

**Input Context:**
- System prompt: [purpose in one sentence]
- Data injected: [table/field names, row limit]
- Input tokens (est.): [n]

**Output:** [Format and key fields returned]

**Output tokens (est.):** [n]

**Gate:** AI module must be active for tenant. Feature slug: `[slug]`.

**Fallback:** [What happens if AI call fails]

**Human Oversight:** [None / Soft confirm / Hard confirm / Mandatory review]

---

### AI Module Gate

This module's AI features are **disabled by default** for all tenants. They activate only when:

1. The tenant has purchased an AI add-on tier (Starter / Growth / Enterprise).
2. The specific feature slug is enabled in `tenant_ai_features`.
3. The tenant's monthly budget has not been exhausted (`BudgetGuard` check passes).

Users without an active AI module see no AI UI elements. The application does not make any AI API calls for ungated tenants.

**Admin control:** Tenant administrators can enable/disable individual AI features within their tier via the AI Module settings screen.

---

### Token Cost Model

| Feature | Calls/User/Day | Input Tokens | Output Tokens | Cost/User/Month (USD) |
|---------|---------------|-------------|--------------|----------------------|
| [name] | [n] | [n] | [n] | $[n] |
| **Total** | | | | **$[n]** |

**Cost assumptions:** [model name], [usage scenario], no caching.

**With caching applied (est. [X]% hit rate):** $[n]/user/month.

**Recommended AI module tier for this module:** [Starter / Growth / Enterprise]

**Suggested retail contribution (UGX):** [n] per tenant per month (included in tier pricing).

*Full cost model: see `projects/[ProjectName]/_context/ai-cost-model.md` and `ai-cost-modeling` skill.*

---

### AI Architecture

**Pattern:** [Direct API / RAG / Function Calling / Streaming]

**Provider:** [Anthropic / OpenAI / DeepSeek / Gemini]

**Integration layer:**
- Gate: `AIGate::check(tenantId, featureSlug)` — throws if module inactive
- Budget Guard: `BudgetGuard::assertAvailable(tenantId)` — throws if budget exhausted
- Provider: `AIProvider::complete(AIRequest)` — provider-agnostic interface
- Metering: `AIUsageLog::record(...)` — logs every call to token ledger

**Metering:** Every AI call in this module is recorded in `ai_usage_log` with `tenant_id`, `user_id`, `feature_slug`, `model`, `input_tokens`, `output_tokens`, and `cost_usd`.

*Architecture detail: see `ai-architecture-patterns` skill.*

---

### AI UX Design

**Loading state:** [Skeleton / spinner / streaming — specify per feature]

**Result display:** [How AI output is shown — card, inline, modal, dashboard widget]

**Confidence indicator:** [Yes / No — if Yes, specify High/Medium/Low mapping]

**Human oversight control:** [Describe confirm dialog or review screen if applicable]

**Error state:** [User-facing message for failure, timeout, budget exceeded]

**Usage visibility:** [Where users see their AI usage — profile / settings / dashboard]

**AI badge:** All AI-generated content is labelled with the ✦ AI badge.

*UX patterns: see `ai-ux-patterns` skill.*

---

### AI Security Posture

- **Input sanitisation:** All user-supplied input passes through `AIInputSanitiser` before prompt construction.
- **PII scrubbing:** [List of fields scrubbed] are stripped before API transmission.
- **Output validation:** AI responses are parsed and validated against the expected schema before display or storage.
- **Audit log:** Every AI call is recorded in `ai_audit_log` with input/output hashes.
- **Rate limiting:** [n] calls/user/hour, [n] calls/tenant/hour.
- **Data classification:** Highest sensitivity field in context: [Public / Internal / Confidential / Special]. [If Special: note that this data is NOT sent to external APIs.]
- **DPPA compliance:** [Applicable / Not applicable]. [If applicable: list consent, retention, and rights FRs.]

*Security checklist: see `ai-security` skill.*

---

### AI Requirements (FR + NFR)

#### Functional Requirements

- **FR-AI-[NNN]-01:** When the tenant's AI module is active and the user triggers [action], the system shall call the AI provider with the specified prompt and display the result within [X] seconds.
- **FR-AI-[NNN]-02:** When the tenant's AI budget for the current month is exhausted, the system shall block further AI calls and display the message: "Your AI usage limit for this month has been reached."
- **FR-AI-[NNN]-03:** The system shall record every AI call to `ai_usage_log` before returning the result to the user.
- **FR-AI-[NNN]-04:** The system shall send an alert to the tenant administrator when AI usage reaches 80% of the monthly budget.

#### Non-Functional Requirements

- **NFR-AI-[NNN]-01:** AI response latency ≤ 8 seconds at P95 for non-streaming features. *[SMART-verified: measurable at P95 under normal load]*
- **NFR-AI-[NNN]-02:** AI module gate check shall add ≤ 10 ms to request latency. *[Achieved via in-memory cache of tenant module status, TTL 60s]*
- **NFR-AI-[NNN]-03:** Token ledger shall record usage with < 1% discrepancy against provider billing statements.
```

---

## Context Files to Create/Update

When generating the AI Integration section, also create or update:

```
projects/<ProjectName>/_context/ai-opportunities.md   ← AI Opportunity Register
projects/<ProjectName>/_context/ai-cost-model.md      ← Token cost calculations
projects/<ProjectName>/_context/ai-features.md        ← Feature blueprints (from ai-feature-spec)
```

---

## V&V Tags for AI Requirements

Use these additional fail tags in AI sections:

- `[AI-GATE-FAIL: feature not gated]` — AI feature makes API calls without module gate check
- `[AI-COST-FAIL: no token estimate]` — FR references AI but has no token cost model
- `[AI-METER-FAIL: no usage log]` — AI call not recorded to ai_usage_log
- `[AI-PII-FAIL: unscubbed field in prompt]` — PII field sent to external API without scrubbing
- `[AI-FR-INCOMPLETE: missing fallback FR]` — AI feature has no failure-mode functional requirement

---

## Quick Reference — Skill Invocation Order

For a complete AI feature, invoke these skills in order:

1. `ai-opportunity-canvas` — identify and rank opportunities
2. `ai-feature-spec` — design each feature
3. `ai-cost-modeling` — calculate token economics and price
4. `ai-architecture-patterns` — design integration layer
5. `ai-ux-patterns` — design UX states
6. `ai-security` — run security checklist
7. `ai-metering-billing` — design token ledger and billing
8. **`ai-integration-section`** — generate document section (this skill)

---

**See also:**
- `ai-opportunity-canvas` — Source of AI opportunities
- `ai-feature-spec` — Feature blueprint inputs to this section
- `ai-cost-modeling` — Cost model inputs
- `ai-architecture-patterns` — Architecture detail
- `ai-metering-billing` — Metering and billing design
- `ai-security` — Security posture detail