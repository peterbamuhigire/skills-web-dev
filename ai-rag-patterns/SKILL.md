---
name: ai-rag-patterns
description: Use when building features that answer questions from private data, documents,
  policies, or time-sensitive information — RAG architecture, chunking strategies,
  hybrid search, re-ranking, vector databases, evaluation, agentic RAG, multimodal
  RAG...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# RAG Patterns — Retrieval-Augmented Generation

<!-- dual-compat-start -->
## Use When

- Use when building features that answer questions from private data, documents, policies, or time-sensitive information — RAG architecture, chunking strategies, hybrid search, re-ranking, vector databases, evaluation, agentic RAG, multimodal RAG...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-rag-patterns` or would be better handled by a more specific companion skill.
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
## Overview

RAG solves the core LLM limitation: they only know what they were trained on. Use RAG to inject private data (invoices, menus, policies, reports) into every AI response.

**Core principle:** RAG = look up a database + LLM synthesises the results. The LLM never needs to "know" your data.

---

## When to Use RAG

| Condition | Action |
|---|---|
| Knowledge base < 200K tokens (~500 pages) | Include everything in context — no RAG needed |
| Knowledge base > 200K tokens | Use RAG |
| Data changes frequently (menus, prices, stock) | RAG (update documents, not model) |
| Data is private/confidential | RAG (keeps data out of training pipelines) |
| Need source citations | RAG (chunks are traceable to source) |
| Model needs brand voice / domain jargon | Fine-tune instead |

---

## RAG vs Fine-Tuning

| Factor | RAG | Fine-Tuning |
|---|---|---|
| Up-to-date content | ✅ Yes (add docs anytime) | ❌ Stale until retrained |
| Hallucinations | ✅ Lower (document-grounded) | ❌ Higher |
| Source citations | ✅ Yes | ❌ No |
| Brand voice control | ❌ Weak | ✅ Strong |
| Domain jargon | ❌ Weak | ✅ Strong |
| Up-front cost | ✅ Lower | ❌ High |

**Default: start with RAG.** Fine-tune only when RAG + prompt engineering cannot deliver the required tone or vocabulary.

---

## Additional Guidance

Guidance is split across two reference files so this entrypoint stays compact.

**[references/skill-deep-dive.md](references/skill-deep-dive.md)** — architecture, chunking, retrieval, schema:

- `Pipeline Architecture`
- `Chunking Strategies`
- `Embedding Model Selection`
- `Vector Database Selection`
- `Retrieval Algorithms`
- `Re-Ranking`
- `Full RAG Query Algorithm`
- `Query Rewriting (Multi-Turn)`
- `RAG Schema (Multi-Tenant)`
- `Evaluation Framework`
- `Production Patterns`
- `Agentic RAG`
- `Multimodal RAG`, `Edge Cases`, `Cost Optimisation`, `Sources`

**[references/production-rag.md](references/production-rag.md)** — the progression from draft to production and the gates before shipping:

- `RAG Maturity Model` — Naive → Advanced → Modular
- `Query Transformation` — HyDE, Multi-Query, Step-Back
- `Contextual Compression`
- `Self-RAG`
- `RAGAS Evaluation` — 4 metrics with production thresholds
- `Embedding Pipeline` — batching, upserts, re-embed triggers, $/1M-token table
- `Cost Management Decision Tree` — concrete dollar figures per branch
- `Failure Mode Playbook` — empty, irrelevant, hallucinated, stale
- `Gates Before Shipping`

Load the production file when building a RAG system that has to pass evaluation gates, survive multi-tenant review, or hit a cost budget under load.
