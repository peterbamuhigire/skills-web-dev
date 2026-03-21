# UX Book Study — Skill Improvements (Batch 5)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Apply knowledge from 6 UX/UI books to upgrade 6 existing skills and create 3 new ones, producing world-class, human-feeling applications that avoid AI slop.

**Architecture:** Parallel-safe markdown edits — all 9 tasks target different files with no overlap. New skills go in new directories; updates add/replace focused sections inside existing SKILL.md files. Each task is self-contained.

**Sources (already read and summarised):**
- Hodent — *What UX Is Really About* (cognitive science, dual-process, biases, dark patterns)
- Enders — *Designing UX Forms* (30+ concrete form rules, every field type, error handling)
- Paduraru — *Roots of UI/UX Design* (8pt grid, 60-30-10, typography, shadows, components)
- Panzarella — *UI/UX Web Design Simply Explained* (mental model, customer journey, conversion)
- Nudelman — *UX for AI* (trust, transparency, avoiding slop, human oversight)
- Klein — *UX for Lean Startups* (hypothesis-driven, validate before build, 5-user research)

**500-line limit:** ALL `.md` files in this repo must stay under 500 lines. Check with `wc -l` after writing.

---

## Task 1: Create `ux-psychology` skill (NEW)

**File:** Create `ux-psychology/SKILL.md`

Foundational cognitive science for design. Referenced by all design skills. Content from Hodent (primary), Paduraru, Panzarella.

**Sections to write:**
1. Frontmatter + when to use
2. Dual-Process Model (System 1 / System 2) — design for System 1 by default
3. Memory (sensory/working/long-term) — working memory limits, conventions, procedural memory
4. Attention — finite resource, change blindness, cognitive load types
5. Perception & Gestalt (proximity, similarity, figure-ground, continuity)
6. Motivation — SDT (competence, autonomy, relatedness); why gamification fails
7. Key Cognitive Biases — curse of knowledge, egocentric bias, IKEA effect, status quo bias, loss aversion
8. Dark Patterns — definition, examples, grey-area patterns, how to distinguish nudges
9. Design Laws — Fitts's Law, Hick-Hyman Law, Von Restorff Effect, Pareto 80/20
10. Key Mantras

**Validation:** `wc -l ux-psychology/SKILL.md` → must be ≤ 500

---

## Task 2: Create `ux-for-ai` skill (NEW)

**File:** Create `ux-for-ai/SKILL.md`

AI interface design framework from Nudelman. Critical for avoiding "AI slop." Use whenever building AI-powered features.

**Sections to write:**
1. Frontmatter + when to use (any AI-powered feature)
2. Core principles — Restate, Calibrate, Explain, Transparent data, Acknowledge mistakes
3. Mental models users hold about AI — algorithm aversion, deskilling, halo effect
4. Making AI feel premium (not sloppy) — domain fine-tuning, stateful AI, context-aware suggestions
5. UI patterns — side panel (preferred) vs overlay (avoid) vs full-page; Promptbooks; Mad Lib config
6. Error states & graceful degradation — Value Matrix, false positive vs false negative costs
7. Human oversight — always provide stop/pause/override; Boeing 737 Max principle
8. Onboarding AI features — "set and forget" for low-stakes; immediate value; cold-start suggestions
9. Agentic AI patterns — accept/reject flows, RBAC for agents, async controls
10. Anti-patterns — replacing experts, accuracy-only optimization, chat-only IA, synthetic users
11. Key mantras

**Validation:** `wc -l ux-for-ai/SKILL.md` → must be ≤ 500

---

## Task 3: Create `lean-ux-validation` skill (NEW)

**File:** Create `lean-ux-validation/SKILL.md`

Klein's hypothesis-driven, waste-eliminating UX process. Use before building any feature to validate it's worth building.

**Sections to write:**
1. Frontmatter + when to use
2. Core philosophy — products as hypotheses, not features; pain-driven design
3. The 3-layer validation sequence — Problem → Market → Product (in that order)
4. Tools for validation before building — ethnographic inquiry, landing page test, fake button test, prototype test
5. User research on a budget — 5-user rule, competitor testing, guerrilla coffee shop testing, interview rules
6. Design the test first — define success metric before designing
7. Metrics that matter — the two layers (what vs why); vanity metrics trap; multi-metric approach
8. Feature prioritisation — ROI graph, pain-first, users-ask-solutions trap
9. Iterative process — 9 tools (problem → test → stories → brainstorm → decide → invalidate → sketch → prototype → test)
10. Common startup UX mistakes — top 10
11. Key mantras

**Validation:** `wc -l lean-ux-validation/SKILL.md` → must be ≤ 500

---

## Task 4: Major update to `form-ux-design/SKILL.md`

**File:** Modify `form-ux-design/SKILL.md`

The existing skill has good bones but is missing 30+ concrete rules from Enders. Key additions:

**Add to Section 1 (Philosophy):** The 3-dimension hierarchy (words > layout > flow). "Start with nothing." A form is a conversation.

**Add to Section 2 (Field Anatomy):**
- NEVER use placeholder text as a label (6 reasons listed)
- NEVER use float labels (4 reasons listed)
- Mark optional fields with "(optional)", not required with asterisks
- "The devil is in the dropdown" — when to use each field type
- Specific rules for: Name, Email, Phone, Date of birth, Sex/Gender, Credit card, Address

**Replace Section 4 Rule on validation** with Enders' nuanced approach:
- Inline validation: use only on very short forms; NEVER fire while typing
- Error messages must do 3 things: what happened, where, how to fix
- Pair colour with icon for errors (never colour alone)
- Error summary at page top with anchor links for long forms

**Add new Section: Gateway Screen** — what to show before the form starts

**Add new Section: Confirmation Screen** — what must appear after submission

**Update Section 5 (Wizard):**
- Never use percentage-based progress
- 3–7 steps maximum; heading on every step
- Never use accordion layouts

**Update DOs/DON'Ts section** with Enders' full anti-pattern list (add 15+ new items)

**Validation:** `wc -l form-ux-design/SKILL.md` → must be ≤ 500. If over, move new field-type rules to `form-ux-design/references/field-types.md`.

---

## Task 5: Update `cognitive-ux-framework/SKILL.md`

**File:** Modify `cognitive-ux-framework/SKILL.md`

The existing skill uses Whalen's 6 Minds model well. Add Hodent's specific contributions:

**Add to Section 3 (Attention Mind):**
- Dual-process model (System 1/2) — design for System 1
- Users are not reading: they are scanning, multitasking, satisficing

**Add to Section 4 (Memory Mind):**
- Working memory limit is 3–4 items (not 7±2 — updated research)
- Every time a user switches context, they lose what they held in working memory
- Procedural memory: breaking conventions forces users back to System 2 — always costly

**Add new Section: Cognitive Biases Designers Must Know:**
- Curse of knowledge — you cannot unsee what you know
- Egocentric bias — you are not your user
- IKEA effect — you overvalue what you built
- Hindsight bias — everything seems obvious after you know the answer
- Confirmation bias — you see the data that confirms your belief

**Add new Section: Dark Patterns Checklist** (8 patterns to avoid + distinction from ethical nudges)

**Update Sources section** to add Hodent's book.

**Validation:** `wc -l cognitive-ux-framework/SKILL.md` → must be ≤ 500

---

## Task 6: Update `webapp-gui-design` visual principles section

**File:** Modify `webapp-gui-design/sections/08-best-practices-aesthetics.md`

The existing section has tech-stack best practices but lacks visual design fundamentals. Add:

**Add section: Visual Design Fundamentals (from Paduraru + Panzarella):**
- 8pt spacing system — all dimensions multiples of 8
- 60-30-10 colour rule — 60% neutral, 30% secondary, 10% accent
- Typography rules: line height = font-size × 1.6; never pure black (#000) on white; sans-serif default
- Dual-layer shadows (core shadow + cast shadow)
- Button states: all 6 required (default, hover, active, progress, focus, disabled)
- Never cover entire viewport in hero sections — reveal next section below fold

**Add section: Dominance, Rhythm, Proximity (Panzarella):**
- Every layout needs one dominant element — size, contrast, or negative space
- Consistent spacing creates rhythm — brain learns the rule and moves on autopilot
- Proximity communicates grouping without borders

**Add section: Mental Model Alignment:**
- Design to match how the user thinks, not how the system works
- Implementation model ≠ mental model

**Validation:** `wc -l webapp-gui-design/sections/08-best-practices-aesthetics.md` → must be ≤ 500

---

## Task 7: Update `jetpack-compose-ui` visual standards

**File:** Modify `jetpack-compose-ui/SKILL.md` — update the Visual Standards table and Core Design Principles section.

**Add / update in Visual Standards table:**
- Never pure black text: use `#1A1A1A` or Material 3 `onBackground`
- Never pure white on black: use `#F5F5F5` or Material 3 `background`
- Line height: body text = font-size × 1.6
- Touch targets: MINIMUM 44dp (currently says 48dp — keep 48dp, note 44dp is absolute floor)

**Add section: Mobile-Specific Rules (from Paduraru):**
- 4px baseline grid for text
- Gutter minimum 16dp; below 16dp is unacceptable
- Forward actions always on the right; back/cancel on the left
- Mobile tabs: max 5; bottom placement
- Affordance through animation: pulse/wiggle to signal interactivity
- Touch target shading: shade the full tappable area around radio buttons and checkboxes

**Add to Design Philosophy:**
- Brains process images 60,000× faster than text — use visuals to communicate primary meaning
- Users form judgments in 90 seconds — colour is the first impression

**Validation:** `wc -l jetpack-compose-ui/SKILL.md` → must be ≤ 500. If over, move to `jetpack-compose-ui/references/design-philosophy.md`.

---

## Task 8: Update `pos-sales-ui-design/SKILL.md`

**File:** Modify `pos-sales-ui-design/SKILL.md`

Add Panzarella's customer journey thinking to inform POS UX design.

**Add section: Customer Journey Stages for POS:**
- Exploration phase — customer is browsing; design for discovery, inspiration, open invitations
- Evaluation phase — customer is comparing; show specs, prices, numeric data side-by-side
- Decision phase — highest stress moment; design for maximum reassurance while driving completion
- Post-decision — celebrate; show receipt summary; provide undo/reprint; reduce buyer's remorse
- For POS: most users are permanently in Decision phase — design accordingly

**Add to existing Core Instructions:**
- One page, one primary action: the checkout button is the business objective — make it dominant
- Predictability reduces perceived wait time: show what happens next at every step
- "If you need to write 'click here,' the design failed" — affordance must be self-evident in POS

**Validation:** `wc -l pos-sales-ui-design/SKILL.md` → must be ≤ 500

---

## Task 9: Update `healthcare-ui-design/SKILL.md`

**File:** Modify `healthcare-ui-design/SKILL.md`

Add Hodent's SDT motivation framework and cognitive load principles for clinical UX.

**Add section: Motivation & Engagement in Clinical UX (Hodent SDT):**
- Clinicians need all 3 SDT needs met: Competence (feel skilled/in control), Autonomy (meaningful choices), Relatedness (sense of shared purpose/team)
- Violating autonomy by forcing rigid workflow creates resistance and workarounds
- Design for competence growth: new staff need more scaffolding; experienced staff need shortcuts
- Relatedness: show context that connects individual actions to patient outcomes

**Add section: Cognitive Load in High-Stress Environments:**
- Clinical settings impose maximum intrinsic load — don't add extraneous load
- Recognition over recall is mandatory: clinicians under stress cannot remember; display everything
- Interruption recovery: save state aggressively; show a "where were you?" resume banner after interruption
- Error prevention is more critical than error recovery: force a pause before irreversible actions (medication orders)

**Add to existing Accessibility:**
- Emotion Mind (Hodent): anxiety reduction = preview outcomes before committing; show totals before final step; allow easy exit without losing progress

**Validation:** `wc -l healthcare-ui-design/SKILL.md` → must be ≤ 500

---

## Task 10: Update CLAUDE.md and README.md

**Files:**
- `CLAUDE.md` — add 3 new skills to repository structure tree
- `README.md` — add 3 new skills to the Full Skill Index under correct categories

**Changes to CLAUDE.md structure tree** (add after `lean-ux-validation` does not exist yet — add after `api-testing-verification`):
```
├── ux-psychology/                   # Cognitive science foundations (dual-process, memory, attention, biases)
├── ux-for-ai/                       # AI interface design (trust, transparency, premium vs slop)
├── lean-ux-validation/              # Hypothesis-driven UX (validate before build, 5-user research)
```

**Changes to README.md** — add to Design & UX section:
- ux-psychology
- ux-for-ai
- lean-ux-validation

**Validation:** `wc -l CLAUDE.md` → must be ≤ 500

---

## Task 11: Commit all changes

```bash
git add -A
git status  # verify only expected files
git commit -m "feat: apply book study improvements — Batch 5 (UX psychology, AI UX, lean validation + 6 skill upgrades)"
```

Expected changed files:
- `ux-psychology/SKILL.md` (new)
- `ux-for-ai/SKILL.md` (new)
- `lean-ux-validation/SKILL.md` (new)
- `form-ux-design/SKILL.md` (updated)
- `cognitive-ux-framework/SKILL.md` (updated)
- `webapp-gui-design/sections/08-best-practices-aesthetics.md` (updated)
- `jetpack-compose-ui/SKILL.md` (updated)
- `pos-sales-ui-design/SKILL.md` (updated)
- `healthcare-ui-design/SKILL.md` (updated)
- `CLAUDE.md` (updated)
- `README.md` (updated)
- `docs/plans/2026-03-21-ux-book-study-improvements.md` (new)

---

## Execution Order

Tasks 1, 2, 3 (new skills) and Tasks 4-9 (skill updates) are ALL independent — they touch different files. Run in parallel for maximum speed.

Task 10 (docs update) can run in parallel with 1-9.

Task 11 (commit) runs last, after all others complete.
