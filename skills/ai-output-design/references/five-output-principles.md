# The Five Output Principles — Expanded

Clear, Verifiable, Grounded, Actionable, Adjustable. Each principle, its failure mode, its UI mechanic, and don't-do examples.

---

## 1. Clear

**Failure mode:** unstructured slab of prose. User has to re-read to find the actionable bit.

**UI mechanic:**

- System prompt enforces a structure template.
- Render sections with headings.
- For long outputs, collapse lower-priority sections (Notes, Sources) behind accordions.
- Preserve structure on copy: copying a section should carry the heading.

**Baseline template:**

```
Title
Intro (1-2 sentences)
Key Concepts (bullets)
Steps (numbered, if procedural)
Notes (caveats, limits, edge cases)
Sources (inline + consolidated)
```

**Don't-do:** 800-word wall of text with no headings, even if every sentence is useful.

**Don't-do:** over-enforce — template rigidity that forces "Steps" section on a Q&A with no steps. Use "If a section has no content, omit it."

---

## 2. Verifiable

**Failure mode:** confident-sounding text with no way to check.

**UI mechanic:**

- Inline source markers per claim (Perplexity superscript).
- Consolidated sources panel, sortable.
- "Check this claim" link opens the exact passage.

**Don't-do:** confidence percentage. See `verifiability-patterns.md` for why.

**Don't-do:** a single "Sources" list at the bottom with no mapping back to claims.

---

## 3. Grounded

**Failure mode:** user can't tell what assumptions the AI made.

**UI mechanic:**

- "Why we suggested this" affordance. One click expands.
- Persistent grounding badge: `[Model: Sonnet 4.6] [Mode: Thinking] [Scope: UK law]`.
- Auto-route badges when the model was selected automatically.

**Don't-do:** hide grounding metadata entirely. Users will suspect bias they can't see.

**Don't-do:** dump every metadata field in the main view. Use an expand.

---

## 4. Actionable

**Failure mode:** the response ends and the user has nowhere to go.

**UI mechanic:**

- 2–4 forward affordances per output.
- Affordances are verbs: Save, Export, Cite, Book, Refine.
- Primary affordance is prominent; secondary are iconic.

**Don't-do:** 12 action buttons in a toolbar. Users freeze.

**Don't-do:** hide actions in a three-dot menu when they are the point of the output (e.g. "Book this flight" should be a primary button, not a menu item).

---

## 5. Adjustable

**Failure mode:** user wants a small tweak but has to re-prompt from scratch.

**UI mechanic:**

- On-select inline menu (Shorter / Longer / Simpler / Formal / Translate).
- Augment buttons (Elaborate, Shorten, Make formal).
- Knobs (sliders, dropdowns) above the output.
- Version selector so refinements don't overwrite earlier versions.

**Don't-do:** wipe the previous version on refinement. Always keep siblings.

**Don't-do:** force the user to re-paste the whole input. Refinement should be scoped to selection or to an augmentation directive.
