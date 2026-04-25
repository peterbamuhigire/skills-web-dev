# House-Style Checklist

The 20-point review checklist for any skill (new or legacy). Use this during PR review and during normalisation.

Score: one point per item that passes. 18+ = ready to ship. 15–17 = needs minor fixes. <15 = needs normalisation pass.

## Frontmatter (3 points)

1. `name` matches the directory name (slug).
2. `description` starts with "Use when" and names concrete trigger scenarios.
3. `description` is one line, under 350 characters, no wrapping.

## Structure (5 points)

4. Required sections present in order: title, opening, Prerequisites (if any), When this skill applies, Inputs, Outputs, Non-negotiables (if engineering), Decision rules, core content, Anti-patterns, Read next, References.
5. SKILL.md ≤ 500 lines.
6. No emojis.
7. British English.
8. Every code fence has a language tag.

## Inputs / Outputs contracts (3 points)

9. Inputs table declares every upstream artifact the skill consumes (or explicitly says "None").
10. Outputs table declares every artifact the skill produces, with a link to the template in `skill-composition-standards/references/`.
11. Claimed inputs exist as outputs of a real upstream skill.

## Decision rules (2 points)

12. At least one explicit decision table / ladder with concrete thresholds.
13. Decision rules name the failure mode of the wrong choice, not just the right one.

## Anti-patterns (2 points)

14. Anti-patterns section has 5+ items.
15. Each anti-pattern is concrete (before/after, not principle).

## References + cross-linking (3 points)

16. Every deep topic has its own `references/<topic>.md`.
17. Reference files 150–400 lines each.
18. Read next section names 3–5 adjacent skills.

## Quality (2 points)

19. No stale content (references to deprecated libraries, old framework versions, or out-of-repo skills).
20. No encoding noise (mojibake, smart quotes where ASCII is expected, trailing whitespace).

## Scoring usage

- **18–20:** ready to merge.
- **15–17:** needs targeted fixes. Identify failed items, address in the same PR.
- **10–14:** needs normalisation pass. Run the procedure in `normalisation-playbook.md`.
- **Below 10:** substantial rewrite; consider whether the skill should be split or merged with a neighbour.

## Common first-pass failures on legacy skills

- Missing Inputs / Outputs (items 9–11) — introduce them via Standard 2.
- Anti-patterns listed as principles, not before/after (item 15) — rewrite each.
- Decision rules in prose, not tables (item 12) — extract into table format.
- SKILL.md over 500 lines (item 5) — extract depth into references/.
- No language tags on code fences (item 8) — batch fix with find/replace.

## Running the check

Manual:
- Read SKILL.md top to bottom.
- Tick each box.
- Record the score and the failed items.

Automated (future work):
- A CI script can catch items 1, 2, 3, 5, 6 (emoji detection), 8 (code-fence regex), 18 (heading presence), 20 (encoding).
- Items 4, 7, 9–17, 19 require human review.

Use `quick_validate.py` now for items 1, 2, 3, 5, 6 partially.
