---
name: app-store-review
description: Apple App Store compliance and review readiness for iOS apps. Use when
  preparing App Store Connect submissions, validating App Review Guidelines, privacy
  labels, permissions, In-App Purchases, store listing accuracy, TestFlight testing,
  and...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Apple App Store Review Readiness
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Apple App Store compliance and review readiness for iOS apps. Use when preparing App Store Connect submissions, validating App Review Guidelines, privacy labels, permissions, In-App Purchases, store listing accuracy, TestFlight testing, and...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `app-store-review` or would be better handled by a more specific companion skill.
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
| Release evidence | App Store Connect submission record | Markdown doc covering metadata, screenshots, review notes, and TestFlight status | `docs/ios/app-store-submission-2026-04-16.md` |
| Release evidence | App Store rejection / approval log | Markdown doc tracking review outcomes and remediation | `docs/ios/app-store-review-log.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Overview

Use this skill to ensure iOS apps meet Apple App Store policy and technical requirements before first submission or major updates. Apple uses **human review for every submission**, so focus on completeness, clarity, and compliance to avoid delays and rejections.

## Quick Reference

- App Review Guidelines: completeness, metadata accuracy, design, privacy, IAP rules
- Privacy Labels: declared data types must match actual collection in code
- Info.plist permissions: every key must have a specific, honest usage description
- App Store Connect: screenshots, metadata, URLs, age rating, category
- TestFlight: internal (100 testers) and external (10,000 testers, reviewed)
- Review notes: test credentials, special instructions, permission justifications
- Code signing: certificates, provisioning profiles, entitlements
- Export compliance: ITSAppUsesNonExemptEncryption setting

## Key Differences from Google Play

| Aspect | Google Play | Apple App Store |
|---|---|---|
| Data disclosure | Data Safety Form | App Privacy Labels |
| Console | Play Console | App Store Connect |
| Review type | Automated + manual | Human review always |
| Rollout | Staged rollout % | Phased release (7-day automatic) |
| Testing tracks | Internal / Closed / Open | TestFlight (internal / external) |
| App signing | APK/AAB signing | Code signing + provisioning profiles |
| Payment rules | Flexible in some regions | IAP required for all digital content |

## Additional Guidance

Extended guidance for `app-store-review` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Core Instructions`
- `1. App Review Guidelines (Key Rules)`
- `2. App Privacy Labels (Critical)`
- `3. Info.plist Permissions Audit`
- `4. App Store Connect Configuration`
- `5. TestFlight Testing`
- `6. Review Notes (Critical for First Submission)`
- `Test Account`
- `Key Features to Test`
- `Special Notes`
- `7. Common Rejection Reasons`
- `8. Phased Release`
- Additional deep-dive sections continue in the reference file.