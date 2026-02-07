# Skills Best Practices & Checklist

This guide covers structure requirements, quality standards, and best practices for creating effective skills.

## Structure Requirements

**CRITICAL:** Always follow these structure rules:

✅ **One SKILL.md per skill** (required)
- Each skill is a single SKILL.md file
- No splitting across multiple files

✅ **Keep skills one level deep** in /skills/ directory
- Skills live at `skills/skill-name/SKILL.md`
- Never nest skills deeper (no `skills/category/skill-name/`)

✅ **Subdirectories for detailed content:**

```
skills/skill-name/
├── SKILL.md             # Core patterns (max 500 lines, strictly enforced)
├── references/          # Database schemas, data models (max 500 lines each)
├── documentation/       # Detailed guides (max 500 lines each)
└── examples/            # Code examples, templates, implementations
```

✅ **Skills are self-contained**
- No dependencies between skills
- Each skill loaded independently
- Subdirectories contain supplementary content

See complete file...
