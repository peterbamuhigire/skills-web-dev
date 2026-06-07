---
name: anti-ai-slop
description: NON-NEGOTIABLE real-time guardrail. Apply on EVERY generated output (text, document, UI, code, image brief, social post) continuously as you generate AND before it is delivered, so the output cannot be recognised as "AI slop". Carries the verified definition, the seven universal slop markers each paired with an avoidance rule, the banned-vocabulary list, and a ship-gate checklist. Load first; it overrides stylistic preferences.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - Codex
  - codex
  - generic-agent
  priority: critical
  source: digital-research-engine / ai-slop-detector (2026-06-07), verified per EVIDENCE-AUDIT.md
---

# Anti AI Slop
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

The guardrail that governs **production** — writing/designing/coding so slop never appears in the first place. Detection lives in the companion `ai-slop-audit` skill.

<!-- dual-compat-start -->
## Use When

- Generating ANY output that a person will read, use, or judge: text, document, UI, code, image brief, social post, slide, spec, plan, proposal, or marketing copy. This is a live constraint, not a final-only gate.
- You reach for a banned word, a generic placeholder, an unverified figure, or a template default — stop and correct it in place.

## Do Not Use When

- Never skip it. This skill applies to every generated artefact. If the output is trivial, the ship-gate still takes seconds.

## Required Inputs

- The artefact being produced and its output type (so the right domain block applies).
- Any verifiable facts, names, numbers, citations, packages, or APIs the artefact references.
<!-- dual-compat-end -->

## Real-time application (this is a LIVE constraint, not only a final gate)

Apply these rules **continuously, as you generate** — to every sentence, component, function, slide, or frame at the moment it is written, not only in one pass at the end. The moment you reach for a banned word, a generic placeholder, an unverified figure, or a template default, stop and correct it in place. The ship-gate checklist at the end is the final confirmation, not the first time these rules are consulted. If you are mid-draft and notice slop accumulating, fix it then — do not defer to a cleanup pass.

## What "AI slop" is (so you know what you are preventing)

**AI slop** is low-quality content produced in quantity by generative AI and pushed at people who did not ask for it (Merriam-Webster 2025 Word of the Year, verified). Its three diagnostic properties (Kommers et al., *"Why Slop Matters"*, arXiv 2601.06060, verified):

1. **Superficial competence** — looks fine on the surface, no substance underneath.
2. **Asymmetric effort** — cheap to produce, costly for a human to read/review/fix.
3. **Mass producibility** — generated at volume.

The human tell named in every domain studied: **absence of intent** — the sense that no one *meant* anything by it. Your job is to re-internalise effort (specificity, verification, authored choices) before the artefact reaches a person.

## The seven universal guardrails (apply to EVERY output)

| # | Marker to prevent | Avoidance rule you MUST follow |
|---|---|---|
| **U1** | Genericness / averaging | Every section carries >=1 concrete, named, domain-specific element (real example, number, named entity, decision) a generic template could not produce. Forbid tool defaults. |
| **U2** | Superficial competence | Enforce a substance floor: include a claim, example, number, or decision the artefact could not exist without. If you cannot, the section is filler — cut or replace it. |
| **U3** | Confident wrongness / hallucination | Verify every statistic, citation, quote, named entity, API, and dependency before emit. Cite at the point of claim. Flag uncertainty rather than inventing. |
| **U4** | Volume over substance | Prefer one substantive unit over three hollow ones. Do not pad to length. |
| **U5** | Absence of authored voice / intent | State a point of view, rationale, or named decision. Ban relentless positivity and sycophancy. Allow trade-offs and disagreement. |
| **U6** | Skipping the hard parts | Cover the error/edge/empty cases, counter-arguments, and risks — not just the happy path. |
| **U7** | Mechanical uniformity | Vary sentence length and structure. Break the template. No rule-of-three reflex, no "it's not X, it's Y" formula, no em-dash flood. |

## Banned / high-risk vocabulary (the lexical tells)

These words and constructions are statistically over-produced by LLMs (FSU/COLING-2025; PubMed "delve" +400%). **Do not use them as default register.** A word here is allowed only when it is the genuinely precise term, never as filler.

- **Words:** delve, tapestry, realm, landscape (as metaphor), navigate (as metaphor), leverage, foster, harness, synergy, embark, robust, vibrant, holistic, seamless, intricate, commendable, meticulous, pivotal, underscore, testament, resonate, elevate, paramount, unwavering, multifaceted.
- **Phrases:** "in today's fast-paced world", "in the ever-evolving landscape of", "it is important to note that", "it's worth mentioning", "let's dive in", "here's the kicker", "at the end of the day", "in conclusion", "studies show" (without a named study).
- **Constructions:** the "it's not just X, it's Y" antithesis; reflexive rule-of-three lists; em-dash used to manufacture drama; relentless triplet adjectives ("robust, scalable, and reliable").
- **French equivalents** (for Francophone output): "plongeons dans", "il est important de noter que", "force est de constater", "dans un monde en constante evolution", "par ailleurs/de plus/en outre" as filler connectors, "au coeur de", "pierre angulaire".

## Drop-in guardrail block (inherit in dependent skills)

```
ANTI-SLOP GUARDRAIL (inherit in every output):
1. SPECIFICITY FLOOR — every section carries >=1 concrete, named, domain-specific
   element. No tool defaults, no placeholder copy.
2. VERIFY-BEFORE-EMIT — no statistic, citation, quote, named entity, API, or
   dependency ships unverified; cite at point of claim; flag uncertainty.
3. AUTHORED VOICE — state a point of view / rationale; no relentless positivity,
   no sycophancy; allow trade-offs.
4. COVER THE HARD PARTS — error/edge/empty cases, counter-arguments, risks.
5. BREAK THE TEMPLATE — vary rhythm and structure; forbid default aesthetics and
   the banned-vocabulary list above.
```

## Domain-specific avoidance (load the relevant block for the output type)

- **Written content:** no focal-word clusters; vary sentence length (mix 3-10 with 25-40 words); <=1 em-dash/paragraph; no "in conclusion"; specific examples over generic claims; a stated point of view.
- **UI/UX:** no indigo-500/purple-gradient default; no Inter-only typography; intentional (not uniform) radius/shadow; WCAG contrast >=4.5:1; design ALL states (error/empty/loading/focus/disabled); real testimonials only.
- **Apps/product:** add genuine value over any wrapped API; transparent pricing + in-app cancel; no deceptive AI-capability claims; least-privilege permissions.
- **Code:** verify every imported package exists (no slopsquatting); no placeholder stubs/TODOs in shipped code; parameterised queries; no hardcoded secrets; idiomatic, deduplicated; real tests (not `assert true`); cover edge cases.
- **Image/video:** real specimens only; check anatomy/text/physics; avoid the "AI sheen"; attach provenance (C2PA) where it matters.

## Ship gate (run before delivering ANY output)

- [ ] Every section has >=1 concrete, named, specific element (U1/U2).
- [ ] Every stat, quote, citation, named entity, API, dependency verified (U3).
- [ ] No banned vocabulary used as filler; scanned the output for the list above.
- [ ] The output states a point of view / rationale; no sycophancy (U5).
- [ ] Error/edge/risk cases and counter-arguments addressed (U6).
- [ ] Sentence length and structure varied; no rule-of-three reflex, no antithesis formula, no em-dash flood (U7).
- [ ] Output type's domain block applied.
- [ ] When in doubt, run the `ai-slop-audit` skill on the draft.

If any box is unticked, the output is not ready to ship.

## See also
- `ai-slop-audit` — the detection/evaluation/audit companion (analyse any artefact for slop).
- The host engine's house-style / language-standards skill (apply on top of this).
