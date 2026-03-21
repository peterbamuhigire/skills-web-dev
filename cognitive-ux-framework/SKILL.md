---
name: cognitive-ux-framework
description: "Cognitive science-based UI/UX evaluation framework built on John Whalen's Six Minds model. Use as a standalone evaluation tool or as a cross-cutting reference from webapp-gui-design, pos-sales-ui-design, and healthcare-ui-design skills. Covers visual processing, wayfinding, attention, memory, language, and emotion."
---

# Cognitive UX Framework

## Overview

This skill provides a structured evaluation framework grounded in cognitive psychology and John Whalen's "Design for How People Think" (Six Minds model). It enables systematic assessment of UI/UX decisions against how human cognition actually works.

**Standards:** ISO 9241-210 (Human-centred design), ISO 9241-110 (Interaction principles), WCAG 2.1 (where applicable to cognitive accessibility).

## When to Use This Skill

- Evaluate an existing UI for cognitive usability issues.
- Inform new UI design decisions with cognitive science principles.
- Conduct a cognitive walkthrough of a task flow.
- Assess cognitive load on a per-screen basis.
- Cross-reference from other UI skills (webapp-gui-design, pos-sales-ui-design).

## Quick Reference

| Mind | Core Question | Key Laws/Principles |
|------|--------------|---------------------|
| Vision | Can users perceive the structure? | Gestalt principles, contrast ratios |
| Wayfinding | Can users navigate to their goal? | Information scent, progressive disclosure |
| Attention | Can users focus on what matters? | Hick's Law, Fitts's Law, cognitive load |
| Memory | Can users remember how to use it? | Miller's Law (7 plus/minus 2), recognition over recall |
| Language | Can users understand the words? | Plain language, F/Z reading patterns |
| Emotion | Do users feel confident and in control? | Trust signals, error recovery, feedback timing |

## The Six Minds Framework

### 1. Vision Mind

The Vision Mind governs how users perceive and organize visual information before conscious thought begins.

**Gestalt Principles:**
- **Proximity:** Group related elements close together. Separate unrelated elements.
- **Similarity:** Use consistent visual treatment (color, shape, size) for elements of the same type.
- **Continuity:** Align elements along clear lines or curves to guide the eye.
- **Closure:** Users complete incomplete shapes mentally; use this for icons and logos.
- **Figure-Ground:** Ensure primary content stands out from background. Use whitespace deliberately.

**Visual Hierarchy:**
- Establish a clear reading order through size, weight, color, and position.
- Limit heading levels to three per screen to avoid hierarchy confusion.
- Use contrast ratios of at least 4.5:1 for normal text and 3:1 for large text (WCAG AA).

**Color Psychology:**
- Reserve red exclusively for errors, destructive actions, and critical alerts.
- Use green for success, confirmation, and positive status.
- Apply blue for links, primary actions, and informational states.
- Maintain a maximum of 5 distinct UI colors (excluding grays) per interface.

### 2. Wayfinding Mind

The Wayfinding Mind enables users to build a mental map of the interface and navigate to their goal.

**Information Scent:**
- Every link, button, and menu label shall predict its destination accurately.
- Users abandon paths when scent weakens; keep labels specific (e.g., "Order History" not "Data").

**Navigation Patterns:**
- Provide breadcrumbs for any hierarchy deeper than two levels.
- Display the user's current location in the navigation structure at all times.
- Maintain consistent navigation placement across all pages (ISO 9241-110 consistency).

**Progressive Disclosure:**
- Show only what the user needs at each step.
- Hide advanced options behind expandable sections or secondary menus.
- Reveal complexity gradually as the user's task demands it.

**Landmark Navigation:**
- Use persistent headers, footers, and sidebars as spatial landmarks.
- Keep landmark positions fixed; moving landmarks destroys the user's mental map.

### 3. Attention Mind

The Attention Mind determines what users notice and how much mental effort they expend.

**Hick's Law:** Decision time increases logarithmically with the number of choices.
- Present no more than 7 options per group (aim for 5 or fewer).
- Use categorization to reduce apparent choice count.
- Provide smart defaults to eliminate unnecessary decisions.

**Fitts's Law:** Time to acquire a target depends on distance and target size.
- Make primary action buttons large and place them near the user's current focus.
- Increase clickable/tappable area; minimum 44x44px for touch targets (WCAG 2.5.5).
- Place destructive actions away from primary actions to prevent accidental activation.

**Cognitive Load Theory:**
- **Intrinsic load:** Accept the task's inherent complexity; scaffold it with wizards or step indicators.
- **Extraneous load:** Eliminate unnecessary visual noise, redundant labels, and decorative elements.
- **Germane load:** Maximize learning through consistent patterns, meaningful icons, and clear feedback.

**Dual-Process Model (Kahneman):**
- **System 1** — Fast, automatic, effortless, intuitive. Handles routine decisions, conditioned responses, pattern recognition. Very efficient but deeply biased.
- **System 2** — Slow, deliberate, resource-intensive. Handles complex calculations and effortful reasoning. Does not naturally override System 1.
- Most users interact with your product on System 1. Design for intuitive, low-effort interaction. Do not require deliberate reasoning for routine tasks.
- Satisficing: users stop reading at the point they believe they have enough information. Put critical content first in labels and instructions — never at the end.

**Change Blindness and Inattentional Blindness:**
- Animate or highlight changes so users notice them (e.g., flash a saved indicator).
- Do not rely on a small icon change alone to communicate status updates.
- Place critical feedback near the user's focal point, not in peripheral UI regions.

### 4. Memory Mind

The Memory Mind dictates how much users can hold in working memory and how they recall interface patterns.

**Miller's Law (7 plus/minus 2):**
- Chunk related information into groups of 5 to 7 items.
- Break long forms into logical sections or multi-step wizards.
- Display phone numbers, codes, and IDs in chunked format (e.g., 555-123-4567).

**Recognition Over Recall:**
- Show recent items, favorites, and suggestions instead of requiring typed input.
- Use dropdowns, auto-complete, and visual pickers over free-text fields.
- Display contextual help inline rather than requiring users to remember documentation.

**Consistency Aids Memory:**
- Reuse the same layout patterns across all pages (ISO 9241-110 consistency).
- Place action buttons in the same position on every screen.
- Use identical terminology for the same concept throughout the application.

**Procedural Memory:**
- Respect established platform conventions (e.g., Ctrl+S to save, swipe to delete).
- Do not reassign well-known shortcuts or gestures to different functions.
- Repeated task flows build muscle memory; keep them stable across releases.

**Working memory is fragile:** Every time a user switches context (tab, interruption, navigation), they lose what was held in working memory. Design for interruption recovery — save state aggressively and show clear "where were you?" cues on return.

**Updated capacity research:** Current evidence suggests working memory holds ~3–4 chunks reliably, not 7±2 (Miller's original estimate). Design accordingly — 3–4 items per group is safer than 7.

## 4b. Cognitive Biases Designers Must Know

These biases affect you as a designer more than they affect users. They cause you to build the wrong thing confidently.

| Bias | What it is | Design implication |
|------|-----------|-------------------|
| **Curse of knowledge** | You cannot unsee what you know; it seems obvious to you | Always test with users who have never seen your product |
| **Egocentric bias** | You assume others experience the world as you do | You are never your user; research is non-optional |
| **IKEA effect** | You overvalue things you helped build | You are a poor judge of your own product's quality |
| **Hindsight bias** | Past outcomes seem more predictable than they were | Bad design decisions looked fine at the time — document your reasoning |
| **Confirmation bias** | You seek data that confirms your existing beliefs | Actively look for disconfirming evidence in research |
| **Status quo bias** | Users prefer inaction and existing defaults | Design defaults thoughtfully — they determine most outcomes |

**"You are not your users."** — The cardinal rule of UX. No amount of empathy substitutes for observing real users with your product.

### 5. Language Mind

The Language Mind processes labels, instructions, error messages, and all textual interface content.

**Label Clarity:**
- Use plain language appropriate to the target audience's reading level.
- Replace jargon with familiar terms (e.g., "Save" not "Persist Entity").
- Keep labels to 1-3 words for buttons and menu items.

**Error Messages (three-part rule):**
- State what happened: "Payment failed."
- Explain why: "Your card was declined by the bank."
- Tell users how to fix it: "Try a different card or contact your bank."

**Call-to-Action Wording:**
- Use action-oriented verbs: "Create Account," "Download Report," "Send Invoice."
- Avoid vague labels: "Submit," "OK," "Click Here."
- Match the CTA to the user's mental model of the task outcome.

**Reading Patterns:**
- **F-Pattern:** Place key information along the top and left edge for text-heavy pages.
- **Z-Pattern:** Use for landing pages and sparse layouts; place CTA at the terminal fixation.
- Left-align body text; avoid centered text blocks for anything longer than two lines.

### 6. Emotion Mind

The Emotion Mind shapes trust, confidence, anxiety, and overall user sentiment.

**Error Recovery (Forgiving Design):**
- Provide undo for destructive actions within a 10-second window minimum.
- Use confirmation dialogs only for irreversible or high-impact actions.
- Auto-save user input to prevent data loss on navigation or timeout.

**Progress Indicators:**
- Show step indicators for any process with more than two steps.
- Display progress bars for operations exceeding 2 seconds.
- Provide estimated completion times for long-running processes.

**Feedback Timing (ISO 9241-110 suitability for the task):**
- Visual acknowledgment within 100ms of user action (button state change).
- Meaningful response within 1 second (data loaded or progress shown).
- For operations exceeding 10 seconds, provide progress percentage and allow cancellation.

**Trust Signals:**
- Display security indicators (lock icons, SSL badges) near sensitive inputs.
- Show social proof where appropriate (user counts, testimonials, ratings).
- Maintain visual consistency; broken layouts and inconsistent styles erode trust.

**Anxiety Reduction:**
- Preview outcomes before committing (e.g., "You are about to delete 3 items").
- Show costs, fees, and totals before the final confirmation step.
- Allow easy exit from any flow without losing progress.

## Cognitive Walkthrough Methodology

Use this process to evaluate a specific task flow against the Six Minds.

**Step 1:** Define the user persona (role, experience level, goals, constraints).

**Step 2:** Define the task goal in one sentence.

**Step 3:** List every discrete step the user takes to complete the task.

**Step 4:** For each step, evaluate three questions:
- **Will the user know what to do?** (Wayfinding Mind + Memory Mind)
- **Will the user see how to do it?** (Vision Mind + Attention Mind)
- **Will the user understand the feedback?** (Language Mind + Emotion Mind)

**Step 5:** Score each step: Pass / Minor Issue / Major Issue.

**Step 6:** Generate a findings report sorted by severity, with specific recommendations.

See `references/cognitive-walkthrough-template.md` for the full template.

## Cognitive Load Assessment

Assess each screen or page for the three types of cognitive load.

| Load Type | Definition | Strategy |
|-----------|-----------|----------|
| Intrinsic | Inherent task complexity | Scaffold with wizards, contextual help, progressive disclosure |
| Extraneous | Complexity from poor design | Remove, hide, group, or simplify unnecessary elements |
| Germane | Effort to build mental models | Maximize through consistent patterns, meaningful defaults, visual metaphors |

**Assessment Process:**
1. Inventory all visible elements on the screen.
2. Classify each element as intrinsic, extraneous, or germane.
3. Flag extraneous elements for removal or simplification.
4. Identify intrinsic elements that lack scaffolding.
5. Confirm germane elements use consistent, learnable patterns.

See `references/cognitive-load-assessment.md` for the full assessment framework.

## Standalone Execution

When run as a standalone evaluation:

1. Read the target UI description or screenshots from `../project_context/`.
2. Apply the Six Minds checklist (see `references/six-minds-checklist.md`).
3. Conduct a cognitive walkthrough for primary task flows.
4. Perform cognitive load assessment on key screens.
5. Write the evaluation report to `../output/cognitive_ux_evaluation.md`.

## Cross-Reference Usage

Other UI skills reference this framework by invoking specific sections:

- **webapp-gui-design** references Vision Mind and Attention Mind for layout decisions.
- **pos-sales-ui-design** references Memory Mind and Wayfinding Mind for rapid-use interfaces.
- **healthcare-ui-design** references all six minds with emphasis on Emotion Mind for high-stress contexts.

When referenced, apply only the relevant mind(s) to the calling skill's specific UI context.

## Dark Patterns Checklist

Dark patterns (Brignull): design that intentionally deceives users to extract value at their expense. These are anti-UX and must be avoided.

**Never implement:**
- [ ] Pre-checked subscriptions or opt-ins
- [ ] Confirm-shaming ("No thanks, I don't want to save money")
- [ ] Hidden costs revealed only at payment
- [ ] Obscured or buried cancellation flows
- [ ] Making the desired user action harder to find than the profit-maximising action

**Grey-area patterns to avoid** (exploit cognitive biases at users' expense):
- [ ] Loss aversion exploitation (expiring streaks, "you'll lose your progress")
- [ ] Fabricated scarcity ("only 1 left!" when inventory is plentiful)
- [ ] Opt-out defaults for subscriptions, data sharing, or auto-renewal
- [ ] Bottomless scrolling (removing natural stopping points)
- [ ] Push notifications without genuine user value

**How to distinguish a nudge from a dark pattern:**
A nudge changes behaviour for the long-term benefit of the user or society. A dark pattern changes behaviour for business benefit at the user's expense. The test: *whose interests are actually served?*

## References

- `references/six-minds-checklist.md` — Per-mind evaluation checklist with pass/fail criteria.
- `references/cognitive-walkthrough-template.md` — Step-by-step walkthrough template.
- `references/cognitive-load-assessment.md` — Cognitive load classification and reduction strategies.

## Sources

- Whalen, John. "Design for How People Think." O'Reilly Media, 2019.
- ISO 9241-210:2019. Ergonomics of human-system interaction -- Human-centred design.
- ISO 9241-110:2020. Ergonomics of human-system interaction -- Interaction principles.
- Miller, G.A. "The Magical Number Seven, Plus or Minus Two." Psychological Review, 1956.
- Hick, W.E. "On the Rate of Gain of Information." Quarterly Journal of Experimental Psychology, 1952.
- Fitts, P.M. "The Information Capacity of the Human Motor System." Journal of Experimental Psychology, 1954.
- Hodent, C. (2022). *What UX Is Really About.* CRC Press.
- Kahneman, D. (2011). *Thinking, Fast and Slow.* Farrar, Straus and Giroux.
