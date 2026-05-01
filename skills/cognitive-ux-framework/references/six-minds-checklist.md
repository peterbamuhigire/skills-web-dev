---
name: six-minds-checklist
description: "Per-mind evaluation checklist with pass/fail criteria for the Cognitive UX Framework."
---

# Six Minds Evaluation Checklist

Use this checklist to evaluate a UI screen or component against each cognitive mind. Mark each criterion as Pass, Fail, or N/A. Failed items require a recommendation note.

## How to Use

1. Identify the screen, page, or component under evaluation.
2. Walk through each mind's criteria in order.
3. Record Pass/Fail/N/A for every item.
4. For each Fail, write a specific recommendation.
5. Tally results per mind and overall.

## Scoring

- **Pass:** The criterion is fully satisfied.
- **Fail:** The criterion is not met; document the specific deficiency.
- **N/A:** The criterion does not apply to this screen or component.

**Severity Classification:**
- 3+ Fails in a single mind = **Critical** — that mind is poorly served.
- 1-2 Fails in a single mind = **Moderate** — targeted fixes needed.
- 0 Fails = **Strong** — that mind is well served.

---

## 1. Vision Mind Checklist

| # | Criterion | Pass/Fail/N/A | Notes |
|---|-----------|---------------|-------|
| V1 | Clear visual hierarchy exists (primary, secondary, tertiary levels distinguishable) | | |
| V2 | Related items use proximity grouping (Gestalt proximity principle) | | |
| V3 | Text contrast ratio meets WCAG AA minimum (4.5:1 normal text, 3:1 large text) | | |
| V4 | Icons are universally recognizable or paired with text labels | | |
| V5 | Color is not the sole means of conveying information (WCAG 1.4.1) | | |
| V6 | Visual similarity is used consistently (same style for same element type) | | |
| V7 | Figure-ground distinction is clear (content stands out from background) | | |
| V8 | Whitespace separates logical sections effectively | | |
| V9 | No more than 3 heading levels are used per screen | | |
| V10 | Maximum of 5 distinct UI colors (excluding neutrals) are used | | |

**Vision Mind Score:** ___ Pass / ___ Fail / ___ N/A

---

## 2. Wayfinding Mind Checklist

| # | Criterion | Pass/Fail/N/A | Notes |
|---|-----------|---------------|-------|
| W1 | User can identify their current location in the navigation structure | | |
| W2 | Navigation is consistent in position and structure across pages | | |
| W3 | Breadcrumbs are present for hierarchies deeper than 2 levels | | |
| W4 | Information scent is strong (labels accurately predict destination content) | | |
| W5 | Back/return navigation is available and functions predictably | | |
| W6 | Progressive disclosure hides advanced options until needed | | |
| W7 | Spatial landmarks (header, sidebar, footer) remain fixed across pages | | |
| W8 | Search is available and returns relevant results with clear scent | | |
| W9 | Primary task flow requires no more than 3 clicks/taps from entry point | | |
| W10 | Error states provide a clear path back to the intended flow | | |

**Wayfinding Mind Score:** ___ Pass / ___ Fail / ___ N/A

---

## 3. Attention Mind Checklist

| # | Criterion | Pass/Fail/N/A | Notes |
|---|-----------|---------------|-------|
| A1 | Cognitive load is managed (no more than 7 items per group, aim for 5) | | |
| A2 | Primary action is visually dominant on the screen | | |
| A3 | Visual distractions are minimized (no unnecessary animations, ads, decorations) | | |
| A4 | Hick's Law is applied (choices are reduced or categorized) | | |
| A5 | Fitts's Law is applied (primary targets are large and near focus) | | |
| A6 | Touch/click targets meet minimum 44x44px | | |
| A7 | Changes and updates are visually highlighted (avoids change blindness) | | |
| A8 | Critical feedback is placed near the user's focal point | | |
| A9 | Destructive actions are separated from primary actions spatially | | |
| A10 | Smart defaults are provided to reduce unnecessary decisions | | |

**Attention Mind Score:** ___ Pass / ___ Fail / ___ N/A

---

## 4. Memory Mind Checklist

| # | Criterion | Pass/Fail/N/A | Notes |
|---|-----------|---------------|-------|
| M1 | UI relies on recognition, not recall (options are visible, not memorized) | | |
| M2 | Defaults are provided for common values | | |
| M3 | Layout is consistent across all pages of the same type | | |
| M4 | Common interaction patterns are reused (same action = same gesture) | | |
| M5 | Information is chunked into groups of 5-7 items | | |
| M6 | Recent items, favorites, or history are surfaced for repeat tasks | | |
| M7 | Terminology is identical for the same concept throughout the app | | |
| M8 | Platform conventions are respected (standard shortcuts and gestures) | | |
| M9 | Long forms are broken into logical sections or steps | | |
| M10 | Contextual help is inline, not hidden in external documentation | | |

**Memory Mind Score:** ___ Pass / ___ Fail / ___ N/A

---

## 5. Language Mind Checklist

| # | Criterion | Pass/Fail/N/A | Notes |
|---|-----------|---------------|-------|
| L1 | Labels are clear and free of jargon for the target audience | | |
| L2 | Error messages follow the three-part rule (what / why / how to fix) | | |
| L3 | CTAs use action-oriented verbs ("Create Order," not "Submit") | | |
| L4 | Reading level is appropriate for the intended user base | | |
| L5 | Key content follows F-pattern or Z-pattern layout for the page type | | |
| L6 | Button and menu labels are 1-3 words | | |
| L7 | Body text is left-aligned (no centered text blocks beyond 2 lines) | | |
| L8 | Instructions use active voice ("Enter your email" not "Email should be entered") | | |
| L9 | Placeholder text supplements, not replaces, labels | | |
| L10 | Confirmation messages state exactly what was accomplished | | |

**Language Mind Score:** ___ Pass / ___ Fail / ___ N/A

---

## 6. Emotion Mind Checklist

| # | Criterion | Pass/Fail/N/A | Notes |
|---|-----------|---------------|-------|
| E1 | Undo is available for destructive actions (minimum 10-second window) | | |
| E2 | Progress indicators are present for multi-step processes | | |
| E3 | Trust signals are visible near sensitive inputs (security icons, SSL) | | |
| E4 | Visual feedback is immediate (within 100ms of user action) | | |
| E5 | Meaningful response appears within 1 second of action | | |
| E6 | Operations exceeding 10 seconds show progress and allow cancellation | | |
| E7 | Confirmation dialogs preview outcomes before committing | | |
| E8 | Users can exit any flow without losing progress (auto-save or draft) | | |
| E9 | Social proof or validation is present where appropriate | | |
| E10 | Visual consistency is maintained (no broken layouts or style mismatches) | | |

**Emotion Mind Score:** ___ Pass / ___ Fail / ___ N/A

---

## Summary Scorecard

| Mind | Pass | Fail | N/A | Status |
|------|------|------|-----|--------|
| Vision | | | | |
| Wayfinding | | | | |
| Attention | | | | |
| Memory | | | | |
| Language | | | | |
| Emotion | | | | |
| **Total** | | | | |

**Overall Assessment:**
- 0-5 total Fails: **Strong** cognitive UX. Address minor items in next iteration.
- 6-12 total Fails: **Moderate** issues. Prioritize by severity and fix before release.
- 13+ total Fails: **Critical** cognitive UX debt. Redesign required for affected areas.

## Next Steps

1. Prioritize all Fail items by severity (Critical > Moderate).
2. Group related Fails by mind for efficient remediation.
3. Apply specific recommendations from the SKILL.md framework.
4. Re-evaluate after changes using this same checklist.
