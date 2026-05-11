---
name: ai-incident-postmortem
description: Use when conducting a blameless postmortem for an AI-specific production incident — the template (timeline, impact, AI-specific RCA categories, contributing-factor map, what went well, what didn't, action items by class), the meeting structure, and the AI-specific action-items catalogue (add golden, change eval gate, add red-team test, pin model, change prompt, tighten retrieval, etc.). Distinct from a generic SRE postmortem because AI incidents need AI-shaped RCA and AI-shaped action items.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Incident Postmortem
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Writing the postmortem document for a closed AI incident (sev-1 and sev-2 always; sev-3 by judgment).
- Designing the AI postmortem template and meeting structure.
- Reviewing whether the action items from past AI incidents have actually shipped.
- Aggregating themes across postmortems for engineering planning.

## Do Not Use When

- The task is the live incident — `ai-incident-response-runbook`.
- The task is the RCA taxonomy itself — `ai-rca-taxonomy`.
- The task is generic platform postmortems — `reliability-engineering` (do not duplicate; reference).

## Required Inputs

- Closed incident with: timeline (from scribe), evidence bundle, mitigation log, comms log.
- RCA taxonomy (`ai-rca-taxonomy`) for category labels.
- Eval harness, prompt registry, model pin registry — to ground proposed action items.

## Workflow

1. Read this `SKILL.md`.
2. Author **the template** (§1) — sections, ownership, format.
3. Run the **meeting** (§2) — agenda, facilitation, blameless rules.
4. Categorise **RCA** (§3) using the taxonomy.
5. Generate **action items** (§4) from the AI-specific catalogue.
6. **Publish + share** (§5) — internal, customer-facing summary, regulator-facing extract.
7. **Track action items** (§6) — close-loop, monthly aggregate.
8. Apply anti-patterns (§7).

## Quality Standards

- Sev-1 and sev-2 postmortems published within 10 business days of incident close.
- Every postmortem has at least one entry against the AI RCA taxonomy.
- Every postmortem produces ≥ 1 action item from the AI-specific catalogue (not just "improve monitoring").
- Action items have a single owner, a due date, and a verification check.
- A monthly aggregate of postmortems is reviewed by AI leadership; recurring root-cause classes drive engineering investment.
- Postmortem is **blameless**: no individuals named as the cause; system and process issues only.

## Anti-Patterns

- Postmortem template borrowed from generic SRE — misses prompt, model, eval, retrieval categories entirely.
- "Root cause: human error" — never an acceptable RCA in a blameless postmortem.
- One action item: "add more monitoring" — useless without specifying which signal at what threshold owned by whom.
- Action items added with no owner and no due date — never close.
- Customer-facing summary copy-pasted from internal; reveals operational detail / partner names that should not be public.
- Postmortems live in a wiki nobody reads; no aggregation; no learning compounded.
- AI generated the postmortem from the timeline — surface-level, no real analysis.

## Outputs

- Per-incident postmortem markdown.
- Customer-facing summary (subset of internal).
- Regulator-facing extract (if applicable).
- Action-item entries with owners and due dates.
- Monthly aggregate report.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Postmortem doc | Markdown | `postmortems/inc-1923.md` |
| Operability | Customer summary | Markdown | `postmortems/inc-1923-public.md` |
| Compliance | Regulator extract | PDF | `comms/inc-1923/regulator/postmortem-extract.pdf` |
| Operability | Action items | DB rows | `ai_postmortem_actions` table |
| Operability | Monthly aggregate | Markdown | `postmortems/monthly/2026-05.md` |

## References

- `references/blameless-template.md` — full markdown template with sections and prompts.
- `references/ai-action-items-catalogue.md` — AI-specific action items with examples.
- Companion: `ai-rca-taxonomy`, `ai-incident-response-runbook`, `ai-incident-evidence-capture`, `ai-eval-harness`, `ai-feature-rollout-and-experimentation`, `ai-prompt-injection-and-tenant-safety`.

<!-- dual-compat-end -->

## §1 Template Sections

The full template lives in `references/blameless-template.md`. Required sections:

1. **Summary** — three-sentence summary (what, impact, root cause class).
2. **Severity** — final classified severity; if it changed during the incident, document why.
3. **Impact** — quantitative: affected requests, tenants, duration, cost-runaway estimate, regulatory exposure.
4. **Timeline** — from scribe's record; UTC; named actors; key moments highlighted (detection, classification, first mitigation, containment, recovery).
5. **Root cause** — primary class from `ai-rca-taxonomy`; explanation of mechanism in 1–3 paragraphs.
6. **Contributing factors** — map: data / model / prompt / retrieval / tool / agent / eval / deploy / monitoring / process; mark each as primary, contributing, or non-contributing.
7. **What went well** — concrete observations of effective response.
8. **What did not go well** — concrete observations of friction.
9. **Action items** — table: id, description, category from catalogue, owner, due, verification check.
10. **Lessons** — generalisable insight, not specific to this incident.
11. **Appendix** — evidence bundle reference, mitigation log, links to comms.

## §2 Meeting Structure

Within 5 business days of incident close, facilitate a 60-minute postmortem meeting.

**Attendees:** incident commander, ops-lead, comms-lead, scribe, product owner for the affected feature, AI lead, security if safety event, legal/DPO if regulator was notified.

**Agenda:**
- 0–5 min: ground rules; blameless framing.
- 5–15 min: walk the timeline.
- 15–30 min: walk the RCA tree to reach the primary class.
- 30–45 min: contributing factors map.
- 45–55 min: action items.
- 55–60 min: lessons, ownership of doc finalization.

The facilitator is **not** the IC and not the ops-lead. Usually a separate engineering manager or principal engineer with no skin in this incident.

## §3 RCA Categorisation

Use `ai-rca-taxonomy/references/taxonomy-and-patterns.md` to assign one primary class and any contributing classes. The catalogue:

- **Model**: regression, deprecation, fine-tune drift, distribution shift, system-message rot, prompt regression.
- **Retrieval**: index drift, chunk-quality drift, embedding-model change, citation drift.
- **Tool / Agent**: tool API change, schema change, tool-vendor outage, indirect prompt injection, action-scope expansion.
- **Eval**: test-set rot, judge drift, golden-set leakage, missing test coverage.
- **Data**: training-data shift, customer-data evolution, ingestion drift.
- **Infra**: gateway routing change, region failover, observability gap.
- **Commercial**: provider price change, rate-limit change, contract change.
- **Process**: missed release gate, deploy without canary, missing approval, oncall handoff gap.

## §4 Action Items

Use `references/ai-action-items-catalogue.md`. Examples by class:

- Model regression → "Pin <feature> to dated model `<model>@<date>`; remove use of `*-latest` references; add eval canary on the next model version."
- Prompt drift → "Add prompt-drift golden covering the failure pattern; require diff-eval pass before any prompt PR merges."
- Retrieval drift → "Add chunk-quality monitor (chunk_len distribution drift > 20% pages on-call); pin embedding model version explicitly."
- Eval drift → "Re-calibrate judge against humans monthly; add judge-vs-human kappa to release gate."
- Jailbreak → "Add the captured prompt to the red-team suite; tighten output classifier on PII patterns; rotate any compromised credentials."
- Cost runaway → "Add per-feature cost soft cap; add price-table-snapshot drift alert."
- Agent action → "Move action X from auto-execute to human-approve; add reversibility check to action gate."
- Provider incident → "Document fallback-chain re-verification cadence; add provider-status auto-alert."

Every action item:
- single owner (name, not team).
- due date.
- verification check (what changes in the world when this is "done").
- linked to the incident.

## §5 Publish + Share

- Internal postmortem: full document, in the postmortem repo.
- Customer-facing summary: a tighter version, no operational detail, no provider names; published if status page included the incident.
- Regulator extract: a curated PDF for any regulator notified, tracked by legal.
- Sev-1 + sev-2: shared with AI leadership and the relevant product/engineering teams within the publication window.

## §6 Action-Item Tracking

- Each action item is a row in `ai_postmortem_actions` with status (`open`, `in_progress`, `done`, `not_doing`).
- Weekly review of open items by AI leadership.
- An action item that misses two due dates without justification re-opens at AI leadership; if still missed at one quarter, the relevant engineering manager is accountable.
- Monthly aggregate: count of incidents by RCA class; aging of open action items; recurring patterns.

## §7 Anti-Patterns

- "Root cause: a developer pushed a bad prompt." Wrong root cause framing — the root cause is the missing pre-merge eval gate.
- One action item ("improve testing") that closes everything without changing anything.
- Postmortem written by the IC who responded — sometimes valuable, often blind-spotted. Bring an outside facilitator.
- Customer-facing summary leaks the provider's name, the exact prompt diff, or internal terminology.
- Action items closed by the same engineer who owns them with no verification.
- Monthly aggregates not reviewed — themes never reach engineering planning.
