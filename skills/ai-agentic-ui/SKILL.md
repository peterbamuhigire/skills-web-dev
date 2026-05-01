---
name: ai-agentic-ui
description: Use when designing UI for agentic AI features — plan visibility, checkpoints,
  rollback, tool-use permissions, progress tiers, and shared-control primitives. Covers
  the five agentic patterns (Reflection, Tool Use, Planning, Multi-agent, ReAct),
  tiered permission frameworks (Claude Code style), and the six checkpoint primitives
  for trustworthy long-running AI actions. Complements ai-ux-patterns (which covers
  single-screen AI components) and ai-agents-tools (which covers the engineering
  side). Based on Macfadyen, *Designing AI Interfaces* (O'Reilly, 2025).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agentic UI
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing UI for agentic AI features — plan visibility, checkpoints, rollback, tool-use permissions, progress tiers, and shared-control primitives.
- The feature plans multi-step work, uses tools, or operates semi-autonomously over seconds-to-minutes.

## Do Not Use When

- The feature is a single-prompt, single-response chat — use `ai-ux-patterns` instead.
- The task is engineering-side tool wiring only — use `ai-agents-tools`.

## Required Inputs

- Feature description including number of steps, side-effect surface, and expected run duration.
- List of tools the agent will call, grouped by read-only / moderate / destructive.
- Rollback scope: what state can be restored and at what granularity.

## Workflow

- Read this `SKILL.md` first, then load referenced deep-dives only when needed.
- Classify the feature against the five agentic patterns; select the matching UI requirement.
- Define the tiered permission policy; draft permission prompts using the three-question template.
- Specify the six checkpoint primitives and the four-tier progress model.
- Produce the wireframe annotations and component specs listed under Outputs.

## Quality Standards

- Every long-running agentic task exposes all six checkpoint primitives.
- Every destructive tool call is prompted every time; read-only tools never prompt.
- Every output from a multi-agent system is attributed to an agent.
- User-facing selectors never expose raw model IDs.

## Anti-Patterns

- Auto-running multi-step destructive actions without plan-preview.
- Silent retries with no iteration counter — users think the agent is stuck.
- Collapsing all reasoning so users cannot audit when needed.

## Outputs

- Agentic UI wireframe annotations.
- Tiered-permission policy document.
- Checkpoint schema.
- Plan-preview component spec.
- Multi-tier progress component spec.

## References

- `references/agentic-patterns.md` — five patterns with UI snippets.
- `references/permission-framework.md` — full tier definitions and prompt copy.
- `references/checkpoint-primitives.md` — six primitives with state-machine notation.
- `references/progress-tiers.md` — the four progress tiers with component specs.
<!-- dual-compat-end -->

## Purpose

An agent is an AI feature that plans multi-step work, uses tools, and operates semi-autonomously over seconds-to-minutes. The UI must expose planning, progress, and control. If your feature is a single-prompt, single-response chat, stop — use `ai-ux-patterns` instead.

---

## Three Principles for Agentic UI

- **Reveal the Plan** before execution for complex or costly tasks. Users consent to the plan, not the prompt. Hide the plan only for trivial tasks (fewer than 3 steps, no external side effects).
- **Prioritize what matters most** with layered information. The default view shows stage + elapsed time + one next action; deeper tiers are on-demand.
- **Design for Shared Control** — every step is interruptible, editable, and rollback-able. The user is a collaborator, not a spectator.

---

## The Five Agentic Patterns

| Pattern | What it does | UI requirement |
|---|---|---|
| Reflection | Agent reviews its own output and corrects | Visible "Reviewing… Found error… Corrected" for high-stakes (finance, medical, legal); silent for low-stakes |
| Tool Use | Agent calls external tools (search, code, API) | Show which tool, what it did, what it returned; tiered permission (see below) |
| Planning | Agent decomposes goal into subtasks | Show decomposed plan before execution; expose branch points for conditional plans; allow plan editing before run |
| Multi-agent | Multiple agents collaborate | Attribute every output by agent ("Analysis by Agent A based on data from Agent B"); surface conflicts as user decision points |
| ReAct | Agent alternates reason-act-observe loop | Iteration counter ("Attempt 3: Trying alternative"); strong escalation path when agent is out of depth (hand-off to user) |

See `references/agentic-patterns.md` for expanded UI snippets.

---

## Tiered Permission Framework (Claude Code Model)

Not every tool call needs approval.

| Tier | Examples | Default behavior | Don't-ask-again scope |
|---|---|---|---|
| Read-only | file reads, web fetch, grep | auto-execute, no prompt | n/a (always allowed) |
| Moderate | shell commands, HTTP POST | prompt on first call | per directory / per session |
| Destructive | file delete, db write, rm -rf, git push force | prompt every time | never — always prompt |

Permission prompts must answer three questions:

- **What** — the exact action, parameters visible.
- **Why** — one-sentence justification from the plan.
- **How to revoke** — "undo this approval in Settings > Permissions".

See `references/permission-framework.md` for full prompt copy.

---

## The Six Checkpoint Primitives

Every long-running agentic task needs all six.

- **Checkpoint** — snapshot of state after each significant step. Named, timestamped. Git-like.
- **Rollback** — one-click return to any checkpoint. Destroys work after the rollback point (confirm first).
- **Intermediate output** — provisional outputs shown between steps. Labeled as provisional. User edits become next-stage input (not overwrite of agent output).
- **Permission** — explicit user consent for side-effect actions. See tiered framework above.
- **Edit/error surface** — a single panel showing agent errors, retries, and user corrections in chronological order.
- **Sources** — every factual claim or external input is attributed with source + access-time + open-link.

See `references/checkpoint-primitives.md` for state-machine notation and example layouts.

---

## Four-Tier Progress Communication

- **Notifications** — topmost info only ("Agent finished" / "Needs permission"). Dismissable.
- **Tier 1 Overview** — stage name, elapsed time, active permissions. One line.
- **Tier 2 Detail** — subtask breakdown, current reasoning (collapsed accordion by default), tool/source references. One panel.
- **Tier 3 Full Record** — complete auditable log for debugging and compliance. Separate view.

Collapse Tier 2 reasoning into accordions by default (Lovable pattern). Users rarely want the raw stream; those who do should get it in one click.

See `references/progress-tiers.md` for component specs.

---

## Model, Tool, and Agent Tier Labels for Users

Don't expose technical model names in selectors.

- Instead of `gpt-4o-2024-11-20` → "Great for quick responses".
- Instead of `claude-sonnet-4-5-thinking-64k` → "Specialized for complex reasoning".
- Auto-routing: display a persistent badge ("Auto-selected: Reasoning model") so the user understands why this response differs from the last.

---

## In-Product Copy: Chatbot vs Agent

A chatbot answers; an agent acts. Use "Ask", "Reply" for chatbot; "Run", "Start", "Execute" for agent. Never mix: "Ask the agent to run the task" is confusing; pick one metaphor.

---

## Anti-Patterns

- Auto-running multi-step destructive actions without plan-preview.
- Spinner for minutes with no intermediate output or ETA.
- Collapsing all reasoning so users can't audit when needed.
- Tool approval prompts that don't say what will happen or how to revoke.
- Silent agent retries (ReAct) with no iteration counter — users think it's stuck.
- Multi-agent outputs with no attribution (user can't tell which agent said what).
- Technical model IDs in user-facing selectors.
- No rollback after an agent has taken a side-effect action.

---

**See also:**

- `ai-ux-patterns` — single-screen AI component patterns.
- `ai-agents-tools` — engineering side of tool wiring.
- `ai-output-design` — output surface design principles.
- `ux-for-ai` — deeper AI trust and transparency principles.
