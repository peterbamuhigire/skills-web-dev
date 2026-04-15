# Normalisation Playbook

How to bring a legacy skill up to `skill-composition-standards`. Aim: one skill per pass, 30–90 minutes each depending on size.

## When to normalise

- Skill fails the 20-point checklist (`house-style-checklist.md`) below 15.
- Skill pre-dates the current baseline (created before `observability-monitoring`, `reliability-engineering`, etc.).
- Skill is high-traffic and the floor matters (frequently loaded by other skills or users).

## Procedure

### Step 1 — Score

Read the current SKILL.md and all its references in one pass.

Run the 20-point checklist. Write the score and the failed items into a working note.

Decide: normalise in place, split, or merge with a neighbour?

- **Normalise in place** when the skill has the right scope but wrong shape.
- **Split** when the skill covers multiple concerns that should be separate skills.
- **Merge** when the skill overlaps substantially with a neighbour and the overlap causes ambiguity.

### Step 2 — Declare contracts

Add or rewrite the Inputs and Outputs sections **first**.

Inputs: ask "what does this skill need from upstream skills to do its job?" List them with the producing skill in parentheses. If the skill has no upstream dependency, say "None — this is a foundational baseline".

Outputs: ask "what does this skill produce that downstream skills can consume?" List each artifact and point at the template in `skill-composition-standards/references/`. If the skill currently produces free-form output, decide the formal artifact type.

This is the hardest step. Do it carefully. Everything downstream depends on it.

### Step 3 — Restructure

Move existing content into the required section order:

1. Title
2. Opening paragraph
3. Prerequisites (if any)
4. When this skill applies
5. Inputs
6. Outputs
7. Non-negotiables (engineering skills)
8. Decision rules
9. Core content
10. Anti-patterns
11. Read next
12. References

Do not delete valuable content. Move it into the right section, rewriting headings as needed.

### Step 4 — Extract depth

Anything longer than a dense page — a code tutorial, a decision matrix with more than a page of supporting text, a comparison table with extensive notes — moves to `references/<topic>.md`.

Each reference file:

- 150–400 lines
- Same no-emoji, British-English, language-tagged-fences rules
- Links back to the parent SKILL.md at the top

### Step 5 — Add decision rules

If the skill currently describes "what to do" without "when one option wins over another", add at least one decision table:

```markdown
```text
Input size < 100 rows AND no joins       -> in-memory processing
Input size 100-100k AND read-heavy       -> cached query
Input size > 100k OR mutating workload    -> streaming with pagination
```
```

Name the failure mode of the wrong choice, not just the right one.

### Step 6 — Add anti-patterns

At least 5 concrete before/after examples. Not principles — code or workflow examples. Each anti-pattern states what to do instead.

Bad (principle):
- "Avoid tight coupling between services."

Good (concrete):
- "Two services sharing a Postgres schema for reads. Fix: each service owns its schema; cross-service reads go through the other service's API."

### Step 7 — Add Read next

Name 3–5 adjacent skills with a one-line explanation of when each applies. This helps the next reader compose this skill with others.

### Step 8 — Clean prose

- Remove emojis.
- Rewrite American spellings to British (color → colour, optimization → optimisation, etc.).
- Add language tags to every code fence.
- Remove encoding noise (mojibake, smart quotes where ASCII is expected).
- Remove stale references (deprecated libraries, removed skills, old framework versions).

### Step 9 — Run validator

```bash
cd ~/.claude/skills
python -X utf8 skill-writing/scripts/quick_validate.py <skill-dir>
```

If validator complains about portable markers, run the dual-compat upgrader:

```bash
python -X utf8 skill-writing/scripts/upgrade_dual_compat.py <skill-dir>
```

### Step 10 — Re-score

Run the 20-point checklist again. Target 18+.

Record the before/after score in the commit message:

```
Normalise <skill-name> against skill-composition-standards.

Score: 12 -> 19
- added Inputs/Outputs contracts
- extracted 3 deep sections to references/
- rewrote anti-patterns from principles to concrete examples
- added decision ladder for <X>
- removed 2 references to deprecated libraries
```

## Worked example — minimal skeleton

For a skill that currently has just prose, start from this skeleton:

```markdown
---
name: my-skill
description: Use when <scenarios> — <what it covers>, <what it does not>.
---

# My Skill

One-sentence purpose.

**Prerequisites:** Load `<parent-skill>` first.

## When this skill applies

- Concrete scenario 1
- Concrete scenario 2
- Concrete scenario 3

## Inputs

| Artifact | Produced by | Required? | Why |
|---|---|---|---|
| ... | ... | ... | ... |

## Outputs

| Artifact | Consumed by | Template |
|---|---|---|
| ... | ... | ... |

## Decision rules

```text
Condition A -> do X
Condition B -> do Y
```

## Core content

(existing valuable content, restructured)

## Anti-patterns

- **Anti-pattern 1:** concrete example. Fix: concrete alternative.
- **Anti-pattern 2:** ...

## Read next

- `adjacent-skill-1` — when to use.
- `adjacent-skill-2` — when to use.

## References

- `references/deep-dive-1.md`
- `references/deep-dive-2.md`
```

## Batch strategy

For a cohort of legacy skills, process in priority order:

1. High-traffic baseline-adjacent skills first (they anchor many others).
2. Cross-cutting skills second (security, performance).
3. Platform specialists third.
4. Domain or case-study skills last.

One skill per pass. Do not batch the rewriting itself; quality drops.
