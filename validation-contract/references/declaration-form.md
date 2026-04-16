# Declaration Form — `## Evidence Produced`

Every specialist skill that produces validation evidence adds this section to its `SKILL.md`, placed between `## Outputs` and `## References`.

## Canonical form

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Threat model | Markdown doc per `skill-composition-standards/references/threat-model.md` | `docs/security/threat-model-checkout.md` |
```

## Column semantics

- **Category** — one of the seven canonical names: `Correctness`, `Security`, `Data safety`, `Performance`, `Operability`, `UX quality`, `Release evidence`. Case-sensitive.
- **Artifact** — the concrete thing the skill produces. Noun phrase, not verb.
- **Format** — either a pointer to an existing template (preferred) or a short inline description. Examples of existing templates: `skill-composition-standards/references/threat-model.md`, `skill-composition-standards/references/runbook.md`, `skill-composition-standards/references/migration-plan.md`.
- **Example** — a realistic path showing where the artifact would live in a project repository.

## Worked example 1 — `advanced-testing-strategy`

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Test plan | Markdown doc per `skill-composition-standards/references/test-plan.md` | `docs/testing/test-plan-checkout.md` |
| Correctness | Latest CI run evidence | CI URL or archived log | `https://ci.example.com/run/12345` |
```

## Worked example 2 — `vibe-security-skill`

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Threat model | Markdown doc per `skill-composition-standards/references/threat-model.md` | `docs/security/threat-model-checkout.md` |
| Security | Abuse-case catalogue | Markdown doc listing misuse scenarios | `docs/security/abuse-cases-checkout.md` |
```

## Worked example 3 — `observability-monitoring` (multi-category)

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | SLO record | Markdown doc per `skill-composition-standards/references/slo.md` | `docs/slo/checkout-service.md` |
| Operability | Runbook | Markdown doc per `skill-composition-standards/references/runbook.md` | `docs/runbooks/checkout-latency.md` |
| Release evidence | Post-deploy verification log | Markdown doc or CI artifact | `docs/releases/2026-04-16-verify.md` |
```

## Common mistakes

- **Declaring every category.** The signal dies when a skill claims to produce evidence for six categories. Pick the categories where the skill actually produces the artifact.
- **Skipping the Format column.** The template pointer is how reviewers know what a "Threat model" should look like. Free-form artifacts without a format pointer are harder to mechanise.
- **Using a category synonym.** `Safety` is not a category. `Reliability` is not a category. Use the exact canonical names.
- **Vague Example paths.** `docs/file.md` is not a useful example. Use a realistic feature-named path.
