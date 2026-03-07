---
name: cognitive-load-assessment
description: "Framework for assessing and optimizing cognitive load on a per-screen basis using intrinsic, extraneous, and germane load classification."
---

# Cognitive Load Assessment Framework

This framework provides a systematic method to inventory, classify, and optimize the cognitive load of any UI screen or page. Based on Sweller's Cognitive Load Theory and applied through the lens of the Six Minds model.

**Standard Reference:** ISO 9241-110:2020 (Interaction principles: self-descriptiveness, conformity with expectations, controllability).

---

## Cognitive Load Theory Summary

Human working memory has a limited capacity. The total cognitive load on a user at any moment is the sum of three types:

| Load Type | Definition | Goal |
|-----------|-----------|------|
| **Intrinsic** | Complexity inherent to the task itself | Cannot eliminate. Scaffold and structure it. |
| **Extraneous** | Complexity added by poor design or unnecessary elements | Must eliminate or minimize. |
| **Germane** | Effort spent building useful mental models and schemas | Should maximize through good design. |

**Key Principle:** When extraneous load is high, it consumes capacity that could serve germane load. Users learn less, make more errors, and abandon tasks more frequently.

---

## Step 1: Screen Element Inventory

List every visible element on the screen under evaluation.

| # | Element | Type | Purpose | Essential? |
|---|---------|------|---------|-----------|
| 1 | | Text / Button / Icon / Image / Input / Link / Indicator / Decoration | | Yes / No |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |
| 9 | | | | |
| 10 | | | | |

Add rows as needed. Count the total number of elements.

**Element Count Guidelines:**
- Fewer than 15 elements: Low density. Likely manageable.
- 15-30 elements: Medium density. Review for extraneous items.
- More than 30 elements: High density. Likely overloaded. Immediate review required.

---

## Step 2: Load Classification

Classify each element from the inventory into one of three load types.

### Intrinsic Load Elements

These elements represent the core task complexity. They cannot be removed without changing the task.

| # | Element | Why Intrinsic | Scaffolding Present? |
|---|---------|--------------|---------------------|
| | | | Yes / No / Partial |
| | | | |
| | | | |

**Examples of intrinsic load:**
- A multi-field form for entering a patient record (the data itself is complex).
- A financial dashboard with multiple KPIs (the domain requires these metrics).
- A code editor with syntax highlighting (code is inherently complex).

### Extraneous Load Elements

These elements add complexity without supporting the task. They are design failures.

| # | Element | Why Extraneous | Recommended Action |
|---|---------|---------------|-------------------|
| | | | Remove / Hide / Group / Simplify |
| | | | |
| | | | |

**Common sources of extraneous load:**
- Decorative images or animations that serve no informational purpose.
- Redundant labels (e.g., a search icon inside a field already labeled "Search").
- Inconsistent navigation patterns that force relearning.
- Unnecessary confirmation steps for low-risk actions.
- Cluttered toolbars with rarely used options shown at the same level as common ones.
- Jargon or technical language that forces users to translate mentally.

### Germane Load Elements

These elements help users build accurate mental models of the system.

| # | Element | How It Aids Understanding | Effective? |
|---|---------|--------------------------|-----------|
| | | | Yes / No / Partial |
| | | | |
| | | | |

**Examples of germane load:**
- Consistent color coding that maps to status (green = active, red = error).
- Meaningful default values that teach expected input formats.
- Visual metaphors that map to real-world concepts (shopping cart, folder).
- Inline help text that explains a field's purpose at the point of need.
- Step indicators that show progress and remaining effort.

---

## Step 3: Reduction Strategies for Extraneous Load

Apply these strategies to every element classified as extraneous.

### Remove

Eliminate the element entirely if it serves no task purpose.

| Candidate Element | Justification for Removal | Risk of Removal |
|-------------------|--------------------------|----------------|
| | | None / Low / Medium |
| | | |

**Remove when:**
- The element is purely decorative.
- The element duplicates information already present.
- No user task depends on the element.

### Hide

Move the element behind a disclosure control (expand, menu, tooltip).

| Candidate Element | Hide Mechanism | Trigger to Reveal |
|-------------------|---------------|-------------------|
| | Accordion / Menu / Tooltip / Modal | |
| | | |

**Hide when:**
- The element is needed by fewer than 20% of users or fewer than 20% of sessions.
- The element supports an advanced or secondary workflow.
- The element is valid but not needed at this point in the task flow.

### Group

Combine related elements into a single visual chunk.

| Elements to Group | Grouping Method | New Label |
|-------------------|----------------|-----------|
| | Card / Section / Tab / Fieldset | |
| | | |

**Group when:**
- Multiple elements relate to the same concept or task step.
- Ungrouped elements exceed Miller's Law threshold (7 plus/minus 2).
- Proximity grouping (Gestalt) clarifies relationships.

### Simplify

Reduce the complexity of the element itself.

| Candidate Element | Current State | Simplified State |
|-------------------|--------------|-----------------|
| | | |
| | | |

**Simplify when:**
- A multi-option control can use smart defaults.
- A complex input can be replaced with a picker or autocomplete.
- Verbose text can be shortened without losing meaning.

---

## Step 4: Scaffolding Strategies for Intrinsic Load

Apply these strategies to intrinsic load elements that lack adequate support.

### Progressive Disclosure

Reveal complexity only as the user's task demands it.

| Complex Element | Disclosure Strategy | Trigger |
|----------------|-------------------|---------|
| | Wizard steps / Expandable sections / Contextual panels | |
| | | |

**Apply when:**
- A form has more than 7 fields.
- A process has more than 3 logical phases.
- Users do not need all information simultaneously.

### Wizards and Step Indicators

Break complex tasks into sequential steps with visible progress.

| Task | Number of Steps | Step Labels |
|------|----------------|-------------|
| | | Step 1: ... / Step 2: ... / Step 3: ... |
| | | |

**Apply when:**
- The task has a natural sequential order.
- Showing all fields at once overwhelms the user.
- Each step can be validated independently before proceeding.

### Contextual Help

Provide explanations at the point of need, not in external documentation.

| Element Needing Help | Help Format | Help Content Summary |
|---------------------|------------|---------------------|
| | Tooltip / Inline text / Help icon with popover | |
| | | |

**Apply when:**
- A field's purpose or expected format is not self-evident.
- Domain-specific terms require explanation for the target audience.
- Users frequently make errors on a specific input.

---

## Step 5: Optimization Strategies for Germane Load

Maximize the user's ability to build accurate, reusable mental models.

### Consistent Patterns

| Pattern | Where Applied | Consistent Across All Pages? |
|---------|--------------|------------------------------|
| Action button placement (e.g., bottom-right) | | Yes / No |
| Color-status mapping | | Yes / No |
| Navigation structure | | Yes / No |
| Form layout | | Yes / No |
| Error display format | | Yes / No |

**Fix any "No" entries.** Inconsistency forces users to relearn, consuming germane capacity unproductively.

### Meaningful Defaults

| Input Field | Default Value | Why Meaningful |
|------------|--------------|---------------|
| | | Matches the most common user choice |
| | | |

**Apply when:**
- One option accounts for more than 60% of selections.
- The default teaches the expected format (e.g., date placeholder).
- Pre-filling reduces the number of decisions the user must make.

### Visual Metaphors

| Concept | Metaphor Used | Universally Understood? |
|---------|--------------|------------------------|
| | | Yes / No |
| | | |

**Apply when:**
- A real-world analogy maps cleanly to the digital interaction.
- The metaphor reduces the need for text explanation.
- The target audience shares the cultural context for the metaphor.

---

## Step 6: Assessment Summary

### Load Distribution

| Load Type | Element Count | Percentage | Target |
|-----------|--------------|-----------|--------|
| Intrinsic | | | Scaffolded |
| Extraneous | | | Near zero |
| Germane | | | Maximized |
| **Total** | | 100% | |

### Action Items

| Priority | Action | Load Type Affected | Effort | Impact |
|----------|--------|--------------------|--------|--------|
| 1 | | Extraneous (remove) | Low/Med/High | High/Med/Low |
| 2 | | Intrinsic (scaffold) | | |
| 3 | | Germane (optimize) | | |
| 4 | | | | |
| 5 | | | | |

### Reassessment Criteria

Re-run this assessment when:
- A screen is redesigned or significantly modified.
- User error rates on the screen exceed the acceptable threshold.
- New features are added to the screen.
- User testing reveals confusion or abandonment on the screen.

---

## Usage Notes

- Assess one screen or page per evaluation. Do not combine screens.
- Involve the target persona from the cognitive walkthrough when classifying load.
- Extraneous load is always the first target for reduction.
- Germane load optimization delivers the highest long-term usability gains.
- This framework pairs with `six-minds-checklist.md` for holistic evaluation.
