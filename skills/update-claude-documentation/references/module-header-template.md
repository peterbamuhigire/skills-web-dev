# Module Header Template (Claude Friendly)

Use this template whenever you refresh a skill's documentation block. Claude loads `name` + `description` from the YAML front-matter and then immediately reads the hero section, so keep this header tight, declarative, and actionable.

---

name: my-skill-name
description: "Briefly describe what the skill does and when to use it so Claude can trigger it automatically in context. Mention core patterns and when to load the skill."
---

# Skill Display Title

## Quick Summary

- Core capability #1
- Core capability #2
- Optional note about constraints or scope

## When to Use

- Use case trigger 1 (phrased as a condition)
- Use case trigger 2
- Use case trigger 3

## Key Patterns (Optional)

- State the primary pattern or workflow
- Reference supporting docs or scripts if needed

## Claude-Friendly Checklist

- [ ] Front-matter `description` mentions specific triggers or scenarios
- [ ] `## Quick Summary` bullets highlight new behavior or focus areas
- [ ] `## When to Use` clearly calls out the contexts Claude should activate the skill
- [ ] Hero title matches the `name` field (natural language display)
- [ ] Any new change mentioned here is also reflected in `CLAUDE.md`

Keep the hero section under about five short paragraphs so Claude can parse the next instructions quickly.
