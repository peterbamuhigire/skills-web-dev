---
name: ai-slop-audit
description: Analyse, evaluate, and audit any artefact for AI slop and score it. Runs after EACH major iteration of work and AUTO-RUNS whenever the user asks to analyse, review, evaluate, audit, critique, or de-slop any project, app, website, business plan, SRS or spec, proposal, blog post, social post, document, image, or codebase, or asks whether something looks AI-generated. Produces a graded slop report giving per-marker findings with severity, evidence, and a concrete fix. Pairs with anti-ai-slop, which prevents slop during production.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - Codex
  - codex
  - generic-agent
  priority: high
  source: digital-research-engine / ai-slop-detector (2026-06-07), verified per EVIDENCE-AUDIT.md
---

# AI Slop Audit
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

The detector. Given any artefact, it decides how much it reads as AI slop, names exactly why, and says how to fix each finding. Production-side prevention is the companion `anti-ai-slop` skill.

<!-- dual-compat-start -->
## Use When

- After EACH major iteration of work on the project at hand — a drafted section, finished feature/module, completed deck, significant revision, or milestone. Log the verdict; block progression on grade F.
- The user asks to analyse, review, evaluate, audit, critique, score, or de-slop any website, web/mobile app, business plan, SRS/spec, proposal/EoI, blog/article, social post, marketing copy, document, image/video, or codebase.
- The user asks "is this AI slop / does this look AI-generated / why does this feel off?".
- As the final gate before publishing or delivering any output.

## Do Not Use When

- There is no concrete artefact to inspect yet — generate it first under `anti-ai-slop`, then audit.

## Required Inputs

- The artefact itself (text, files, screenshots, repo path, or URL) and its claimed purpose/audience.
- For code: access to the dependency manifest so packages can be resolved against their registry.
<!-- dual-compat-end -->

## When this runs

**Cadence — run after EACH major iteration of work on the project at hand.** This is the default mode: whenever a meaningful unit of work is completed — a drafted section, a finished feature or module, a completed slide deck, a significant revision, a milestone — run this audit on what was just produced before moving on. Log the verdict. If the verdict is **F (Blocked)**, do not progress to the next iteration until the blocking findings are fixed. Treat it like a test suite that runs at every checkpoint, not a one-time final review.

**Also auto-run on request:** when the user asks to **analyse, review, evaluate, audit, critique, score, or de-slop** any of: a website, web/mobile app, business plan, SRS or technical spec, proposal/EoI, blog or article, social-media post or campaign, marketing copy, document, image/video, or codebase — or asks "is this AI slop / does this look AI-generated / why does this feel off?".

**Also run as the final gate** before publishing or delivering any engine output.

The companion `anti-ai-slop` skill runs continuously *during* generation; this audit runs *at each checkpoint* to catch what slipped through.

## What slop is (the yardstick)

Low-quality content produced in quantity by AI and pushed at people who did not ask for it (Merriam-Webster 2025 WOTY, verified). Three diagnostic properties (Kommers et al., arXiv 2601.06060): **superficial competence, asymmetric effort, mass producibility**. The human tell: **absence of intent**. You are measuring how strongly an artefact exhibits these.

## Audit method — layered, cheapest first

### Step 1 — Identify artefact type and load the right checklist
Map the artefact to one or more domains: written content (EN/FR), UI/UX, app/product, image/video, code. A "project" (e.g. a website or app) usually spans several — audit each layer.

### Step 2 — Automated gates (🤖, machine-checkable) — any hit is hard evidence
Run every applicable check; a hit on a **blocking** marker (✗) fails the artefact outright.

**Written content**
- 🤖 Focal-word density — delve/tapestry/realm/navigate/underscore/pivotal/intricate/leverage etc. >2 per 500 words.
- 🤖 Em-dash density >1 per paragraph; reflexive rule-of-three; "it's not X, it's Y" repetition; uniform 15-25-word sentences (low burstiness).
- 🤖 Transition clichés ("in today's fast-paced world", "let's dive in", "in conclusion").
- 🤖 Mechanical formatting: Title-Case headers, excess bold, decorative emoji, leftover tool markup ("oaicite", "contentReference").
- ✗ 🤖 Broken/fake citations: dead URLs, invalid DOI/ISBN, fabricated stats, utm_source params copied in.
- French: "plongeons dans", "il est important de noter que", "force est de constater", filler connectors.

**UI/UX**
- 🤖 Indigo/purple-gradient default (HSL 250-280°, sat 70%+); Inter/Roboto/Poppins-only; uniform border-radius; glassmorphism; gradient text; shadcn coloured card-border.
- ✗ 🤖 Dark-mode/body contrast <4.5:1 (WCAG fail).
- ✗ 🤖 Missing states (error/empty/loading/focus/disabled) — state-coverage audit.

**Code**
- ✗ 🤖 Hallucinated/uninstallable imports & packages (slopsquatting) — resolve every dependency against its registry. Package-hallucination is measured, not hypothetical: Spracklen et al. (USENIX Security 2025) found 19.7% of LLM-recommended dependencies did not exist.
- ✗ 🤖 Hardcoded secrets; SQL built by string interpolation; `innerHTML = userInput` (XSS); insecure defaults. AI-generated code fails security checks at scale: Veracode found 45% of AI code samples introduced a known vulnerability, rising to 86% for XSS and 88% for log injection.
- 🤖 Placeholder stubs/TODO/`NotImplementedError`/`...` in shipped code; dead code; duplication; bare-except; cross-language constructs; inconsistent style in one file; tautological tests (`assert true`). Copy-paste/duplication is rising in AI-assisted repos: GitClear measured cloned code blocks up from 8.3% (2020) to 12.3% (2024).

**Image/video**
- 🤖 Missing/contradictory C2PA provenance; SynthID absence (Google-only — absence != authentic); ELA/JPEG-forensics anomalies.

### Step 3 — Structural score (🤖) → 0-100 "genericness"
Combine burstiness, focal-word density, duplication, and template-similarity into a single genericness score. Higher = more slop-like. Report the score and its drivers.

### Step 4 — Human-judgement review (👁) — the checklist no tool replaces
- 👁 **Substance:** what does this assert/decide that required real work? If nothing — slop.
- 👁 **Intent / authored voice:** is there a point of view, or is it relentlessly positive and viewpoint-free?
- 👁 **Specificity:** real named examples/people/numbers, or generic placeholders?
- 👁 **Hard parts:** are errors, edge cases, risks, counter-arguments handled?
- 👁 **Visuals:** anatomy (hands/eyes/teeth), "AI sheen", garbled text-in-image, impossible geometry, video "boiling"/lip-sync.
- 👁 **Product/app:** wrapper with nothing added? fleeceware/dark-pattern billing? deceptive AI claims? fake reviews?
- 👁 **Domain-specific (per artefact):**
  - *Business plan:* fabricated market stats, generic TAM/SAM filler, no authored strategy, "studies show" without a named study.
  - *SRS/spec:* vague requirements, placeholder "Challenges and Future Prospects" sections, missing edge/error specs, hallucinated APIs.
  - *Proposal/EoI:* inflated superlatives, hollow analogies, unverifiable claims, no visible logic (evidence→warrant→implication).
  - *Blog/social:* engagement-bait, no lived experience, clichés, AI-sheen imagery.

## Scoring & verdict

Aggregate into a grade:

| Grade | Meaning | Trigger |
|---|---|---|
| **A — Clean** | No blocking hits; genericness low; substance & intent present | ship |
| **B — Minor slop** | A few automated hits, no blockers; some genericness | fix listed items |
| **C — Slopy** | Multiple automated hits or weak substance/intent | rework before ship |
| **F — Blocked** | Any ✗ blocker (hallucinated fact/citation/package, secret, WCAG fail, missing states) OR no substance at all | do not ship |

## Output format (the audit report)

```
# AI Slop Audit — <artefact name> — <date>
Verdict: <A/B/C/F>   Genericness score: <0-100>
Artefact type(s): <...>

## Blocking findings (✗) — must fix
- [marker] <what was found> · evidence: <quote/line/URL/screenshot ref> · fix: <concrete action>

## Slop findings (by severity)
- [marker] <finding> · evidence: <...> · fix: <...>

## What's good (so it isn't stripped in the fix)
- <substantive, specific, authored elements worth keeping>

## Recommended next step
- <rework / targeted fixes / ship>
```

## Discipline (anti-hallucination — applies to the audit itself)
- Every finding cites concrete evidence from the artefact (a quote, a line number, a colour value, a screenshot region, a URL). No finding without evidence.
- Do not invent a flaw to pad the report. "This artefact is clean" is a valid, wanted verdict.
- Mark inferences "(inference)"; never present a guess as a measured fact.

## See also
- `anti-ai-slop` — prevention companion (write/design/code so slop never appears).
- Host engine house-style skill — apply domain tone on top.
