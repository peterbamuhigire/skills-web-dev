---
name: google-play-store-review
description: Google Play Store compliance and review readiness for Android apps. Use
  when preparing Play Console submissions, validating policies, data safety, permissions,
  ads, IAP, store listing accuracy, and reviewer notes.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Google Play Store Review Readiness

<!-- dual-compat-start -->
## Use When

- Google Play Store compliance and review readiness for Android apps. Use when preparing Play Console submissions, validating policies, data safety, permissions, ads, IAP, store listing accuracy, and reviewer notes.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `google-play-store-review` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Play Console submission record | Markdown doc covering listing, screenshots, content rating, and pre-launch report | `docs/android/play-store-submission-2026-04-16.md` |
| Release evidence | Play Store rejection / approval log | Markdown doc tracking review outcomes and remediation | `docs/android/play-store-review-log.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Overview

Use this skill to ensure Android apps meet Google Play policy and technical requirements before first submission or major updates. Focus on avoiding automated policy flags and making human review fast.

## Quick Reference

- Policy compliance: restricted content, UGC moderation, deceptive UX
- Data Safety: SDK inventory matches form, privacy policy live and accurate
- Permissions: request at point of use, justify sensitive access, no unused permissions
- SDK and tech hygiene: targetSdk current, background work compliant
- Ads and IAP: clear labeling, close controls, pricing and restore flows
- Store listing: screenshots and claims match app
- Reviewer notes: provide test account and step-by-step paths

## Core Instructions

1. Inventory app features and risk areas (ads, UGC, payments, location, kids). Use that to drive policy checks.
2. Audit data collection and sharing for every SDK and permission. Ensure the Data Safety form matches reality.
3. Validate permissions: only declared when used, request at point of use with in-app rationale.
4. Confirm targetSdk and compileSdk and background behavior meet current Play requirements.
5. Verify store listing accuracy: screenshots, video, and descriptions map to real UI and features.
6. Validate monetization: subscriptions, trials, and IAP flows are transparent and functional.
7. Run install and upgrade tests across supported devices and OS versions.
8. Provide detailed Review Notes to guide the reviewer through sensitive flows.

## Key Patterns

### Truthful disclosure

- Keep the Data Safety form, permissions, and privacy policy aligned.
- Treat every SDK as data collection unless proven otherwise.

### Permission gating

- Show a clear in-app rationale before system dialogs.
- Request sensitive permissions only at point of use.
- Provide a fallback if permission is denied.

### Reviewer-friendly submission

- Include a test account, steps to reach sensitive features, and expected results.
- Call out any delays or required setup.

## Reference Files

- references/review-checklist.md: Full Play Store review checklist with code examples and rejection triggers.

## Common Pitfalls

- Declaring "no data collected" while using analytics or crash reporting.
- Requesting permissions that are not used or not justified in the UI.
- Ads that auto-redirect or hide close buttons.
- Store listing screenshots that show non-existent features.
- Missing or inaccessible privacy policy URL.

## Examples

### Review notes template

```markdown
## Test Account
Email: reviewer@example.com
Password: Test1234

## Sensitive Features
1. Location permission: Used for store locator only.
	- Path: Home -> Find Stores
	- If denied, allow manual zip code entry.

## Special Instructions
- First launch may take ~10 seconds to sync catalog.
- Premium features are marked with a star icon.
```
