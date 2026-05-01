---
name: cognitive-walkthrough-template
description: "Step-by-step cognitive walkthrough template for evaluating task flows against the Six Minds framework."
---

# Cognitive Walkthrough Template

This template guides a structured evaluation of a specific user task flow. For each step in the flow, the evaluator assesses whether the user's cognitive needs are met across three dimensions derived from the Six Minds model.

**Standard Reference:** ISO 9241-210:2019 (Human-centred design for interactive systems).

---

## Section 1: Define the Persona

Complete this section before beginning the walkthrough.

| Field | Value |
|-------|-------|
| **Persona Name** | |
| **Role/Title** | |
| **Experience Level** | Novice / Intermediate / Expert |
| **Domain Knowledge** | Low / Medium / High |
| **Technical Literacy** | Low / Medium / High |
| **Primary Goal** | |
| **Key Constraints** | (e.g., time pressure, mobile-only, accessibility needs) |
| **Frequency of Use** | Daily / Weekly / Monthly / One-time |

### Persona Notes

Document any additional context that affects cognitive expectations:
- Age range and any relevant generational technology patterns.
- Environmental factors (noisy, bright, multi-tasking).
- Motivation level (voluntary use vs. required use).
- Prior experience with similar systems.

---

## Section 2: Define the Task Goal

State the task goal in one clear sentence.

| Field | Value |
|-------|-------|
| **Task Goal** | |
| **Starting Point** | (e.g., "User is on the dashboard") |
| **Success Criteria** | (e.g., "Order is saved and confirmation is displayed") |
| **Expected Duration** | |
| **Critical Path?** | Yes / No (Is this a primary business flow?) |

---

## Section 3: List Task Steps

Enumerate every discrete step the user takes from start to completion. A step is one user action (click, type, select, scroll, read).

| Step # | User Action | UI Element | Screen/Page |
|--------|------------|-----------|-------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |

Add rows as needed. Keep steps atomic (one action per row).

---

## Section 4: Per-Step Evaluation Matrix

For each step, answer three cognitive questions. These map to mind pairs:

| Question | Minds Assessed | What to Look For |
|----------|---------------|-----------------|
| Will the user know what to do? | Wayfinding + Memory | Clear navigation, visible options, consistent patterns, recognition over recall |
| Will the user see how to do it? | Vision + Attention | Visual hierarchy, target size, proximity to focus, minimal distraction |
| Will the user understand the feedback? | Language + Emotion | Clear messaging, immediate response, trust signals, error recovery |

### Evaluation Table

| Step # | Will they know what to do? | Will they see how to do it? | Will they understand feedback? | Severity | Recommendation |
|--------|---------------------------|---------------------------|-------------------------------|----------|----------------|
| 1 | Pass / Minor / Major | Pass / Minor / Major | Pass / Minor / Major | | |
| 2 | Pass / Minor / Major | Pass / Minor / Major | Pass / Minor / Major | | |
| 3 | Pass / Minor / Major | Pass / Minor / Major | Pass / Minor / Major | | |
| 4 | Pass / Minor / Major | Pass / Minor / Major | Pass / Minor / Major | | |
| 5 | Pass / Minor / Major | Pass / Minor / Major | Pass / Minor / Major | | |
| 6 | Pass / Minor / Major | Pass / Minor / Major | Pass / Minor / Major | | |
| 7 | Pass / Minor / Major | Pass / Minor / Major | Pass / Minor / Major | | |
| 8 | Pass / Minor / Major | Pass / Minor / Major | Pass / Minor / Major | | |

### Severity Definitions

- **Pass:** The user will succeed at this step without confusion or delay.
- **Minor Issue:** The user may hesitate or need a moment to figure it out, but will succeed. Fix in a future iteration.
- **Major Issue:** The user is likely to fail, abandon the task, or make a consequential error. Fix before release.

### Evaluation Guidance

When assessing "Will they know what to do?" consider:
- Is the next action obvious from the current screen state?
- Does the user's mental model (from experience or training) predict this step?
- Are there competing options that create ambiguity?
- Does the UI rely on recall or recognition?

When assessing "Will they see how to do it?" consider:
- Is the target element visually prominent?
- Is it in a location the user's eye naturally travels to?
- Is the clickable/tappable area large enough?
- Are there visual distractions competing for attention?

When assessing "Will they understand the feedback?" consider:
- Does the system respond within 100ms (visual) and 1s (meaningful)?
- Does the feedback clearly indicate success, failure, or progress?
- If an error occurred, does the message explain what, why, and how to fix?
- Does the user feel confident that their action was registered?

---

## Section 5: Summary Scoring

### Step-Level Summary

| Metric | Count |
|--------|-------|
| Total Steps Evaluated | |
| Steps with All Pass | |
| Steps with Minor Issues | |
| Steps with Major Issues | |

### Mind-Pair Summary

| Mind Pair | Total Pass | Total Minor | Total Major |
|-----------|-----------|-------------|-------------|
| Wayfinding + Memory (know what to do) | | | |
| Vision + Attention (see how to do it) | | | |
| Language + Emotion (understand feedback) | | | |

### Overall Task Flow Rating

- **Green:** 0 Major Issues, fewer than 3 Minor Issues. Flow is cognitively sound.
- **Yellow:** 0 Major Issues, 3 or more Minor Issues. Flow works but causes friction.
- **Red:** 1 or more Major Issues. Flow has cognitive failure points that require redesign.

---

## Section 6: Prioritized Findings

List all non-Pass findings in priority order (Major first, then Minor).

### Finding 1

| Field | Value |
|-------|-------|
| **Step #** | |
| **Severity** | Major / Minor |
| **Mind Pair Affected** | |
| **Issue Description** | |
| **User Impact** | |
| **Recommendation** | |
| **Effort Estimate** | Low / Medium / High |

### Finding 2

| Field | Value |
|-------|-------|
| **Step #** | |
| **Severity** | Major / Minor |
| **Mind Pair Affected** | |
| **Issue Description** | |
| **User Impact** | |
| **Recommendation** | |
| **Effort Estimate** | Low / Medium / High |

### Finding 3

| Field | Value |
|-------|-------|
| **Step #** | |
| **Severity** | Major / Minor |
| **Mind Pair Affected** | |
| **Issue Description** | |
| **User Impact** | |
| **Recommendation** | |
| **Effort Estimate** | Low / Medium / High |

Duplicate the finding block as needed for additional issues.

---

## Section 7: Sign-Off

| Field | Value |
|-------|-------|
| **Evaluator** | |
| **Date** | |
| **Task Flow Evaluated** | |
| **Overall Rating** | Green / Yellow / Red |
| **Re-evaluation Needed?** | Yes / No |
| **Re-evaluation Date** | |

---

## Usage Notes

- Conduct one walkthrough per task flow. Do not combine multiple tasks.
- Use the persona consistently; do not switch perspectives mid-walkthrough.
- When in doubt about a severity rating, escalate to Major.
- Re-evaluate after implementing recommendations to confirm resolution.
- This template pairs with `six-minds-checklist.md` for screen-level evaluation.
