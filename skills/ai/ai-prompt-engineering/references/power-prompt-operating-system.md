# Power Prompt Operating System

Self-contained synthesis prepared from the supplied prompt and AI adoption source material. It converts prompt-writing advice into reusable operating rules for production prompts and team prompt libraries.

## Table Of Contents

- Prompt order form
- Prompt matrix
- Team prompt library
- Meeting, email, and document workflows
- AI adoption cycle
- Prompt evaluation

## Prompt Order Form

Before writing a prompt, capture the order:

| Field | Question |
|---|---|
| Outcome | What decision, draft, artifact, or action should the prompt produce? |
| Audience | Who will read or use the result? |
| Source material | What facts, files, transcript, screen, or data must ground the output? |
| Constraints | Length, tone, format, language, compliance, brand, and market limits |
| Examples | What does good output look like? What should be avoided? |
| Review gate | Who checks the result and what must pass before use? |

Do not ask the model to solve ambiguous work the human has not framed.

## Prompt Matrix

Use this matrix to choose the prompt pattern:

| Task type | Prompt pattern | Extra control |
|---|---|---|
| Summarise | Role + source + audience + length + decision focus | "Only use supplied material" |
| Draft | Role + objective + audience + style + examples | Include outline before prose |
| Analyse | Criteria + evidence + countercase + implication | Require assumptions and confidence |
| Transform | Input format + output format + mapping rules | Add schema/checklist |
| Compare | Options + criteria + weights + recommendation rule | Require tradeoffs |
| Plan | Goal + constraints + milestones + risks + owner | Require dependencies |
| Extract | Field schema + source boundaries + missing-data rule | Validate against schema |

## Team Prompt Library

A team prompt is an operational asset, not a personal trick. Store:

- prompt name and owner
- use case and audience
- current version and change note
- required inputs
- model/tool assumptions
- example input and approved output
- quality checklist
- known failure modes
- review cadence

Retire prompts that are unused, unsafe, obsolete, or consistently rewritten by users.

## Meeting, Email, And Document Workflows

- Meeting notes: transcribe, extract decisions/actions/risks/questions, assign owners, then verify against transcript before distribution.
- Email: use the 3B rule in adapted form: brief, balanced, and business-specific. State purpose, context, action needed, and deadline.
- Long documents: ask for outline, then section-by-section drafting. Require source-grounded claims and a final consistency pass.
- Screenshots/images: use visual input to describe state, extract visible facts, identify issue, and propose next action. Do not infer hidden facts.
- Word-count control: set length explicitly and require the model to prioritise the top decision-relevant points.

## AI Adoption Cycle

Use a five-cycle adoption loop:

1. Discover repetitive work and current pain.
2. Draft prompt and examples.
3. Test on real cases.
4. Save the reusable prompt with owner and review gate.
5. Measure time saved, quality improvement, and rework.

The goal is not more prompts. The goal is fewer, better prompts that reliably improve a workflow.

## Prompt Evaluation

Every reusable prompt should have:

- 5 to 10 normal test cases.
- 3 messy or incomplete cases.
- 3 adversarial or policy-sensitive cases.
- A rubric for correctness, usefulness, tone, format, safety, and evidence.
- A baseline output to compare against after prompt or model changes.

Do not promote a prompt to team use until it passes realistic tests and has a known escalation path.
