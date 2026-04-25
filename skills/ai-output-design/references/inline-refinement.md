# Inline Refinement Patterns

Four mechanics for adjusting AI output without re-prompting from scratch.

---

## 1. On-Select UI (Notion Pattern)

User highlights a span of output text. A floating inline menu appears.

**Menu items:**

- Shorter.
- Longer.
- Simpler.
- More formal.
- Translate -> (submenu).
- Rewrite with my own instruction (opens inline text input).

**Behaviour:**

- The action runs a scoped prompt on just the selected span.
- The rest of the output is untouched.
- Result replaces the selection with an undo affordance.

**System prompt scope:**

```
Rewrite only the highlighted span. Preserve surrounding context.
Instruction: {shorter | longer | simpler | formal | translate:<lang> | <user text>}
Highlighted span: """{selection}"""
Surrounding context: """{previous paragraph}...{next paragraph}"""
```

---

## 2. Prompt Augmentation Buttons (Elaborate / Shorten)

Buttons appended to the output that re-run the **last prompt** with an appended directive.

**Typical buttons:**

- Elaborate — "Expand this response with more detail."
- Shorten — "Cut this response to half its length."
- Make formal — "Rewrite in a formal tone."
- Make casual — "Rewrite in a casual tone."
- Add examples — "Add 2 concrete examples."

**Behaviour:**

- User does not retype anything.
- System appends the directive to the last prompt and re-runs.
- Result appears as a new version, not a destructive overwrite.

---

## 3. Knobs (Persistent Controls)

Sliders or dropdowns above the output that parameterise generation. QuillBot is the canonical example.

**Typical knobs:**

- Fluency: Standard ↔ Fluent.
- Formality: Casual ↔ Formal.
- Length: Terse ↔ Verbose.
- Creativity: Conservative ↔ Creative.

**Behaviour:**

- Changing a knob regenerates the output.
- Current knob state is visible and persistent for the session.
- Regeneration produces a new version; previous versions accessible via selector.

**Guardrails:**

- Limit to 3–4 knobs. More is overwhelming.
- Use simple labels, not raw parameters ("Creativity", not "temperature=0.9").

---

## 4. Version Selector (Claude Artifacts Pattern)

Every regeneration creates a sibling version, not a destructive overwrite.

**UI:**

- Version dropdown or side panel showing timestamped versions.
- Each version has an auto-generated label ("v3 — after Elaborate") or a user-typed label.
- Diff between any two versions.
- Restore: creates v_N+1 from an older version's content.

**Rules:**

- Never silently discard a version. The user deletes explicitly.
- On a new chat turn or a major refinement, auto-create a new version.
- Limit history to a sane cap (e.g. last 20) with archive for older.

---

## Combining the Four Mechanics

Most good output surfaces use all four:

- Knobs set the base tone.
- Augmentation buttons produce broad-stroke variants.
- On-select refines local text.
- Version selector keeps everything recoverable.

Do not make the user choose the mechanism — expose them together, and let the user pick the right tool for the edit at hand.
