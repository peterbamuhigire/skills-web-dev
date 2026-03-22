---
name: interaction-design-patterns
description: Use when designing interfaces, building UX flows, choosing layouts, or making navigation decisions. Covers Tidwell's 45+ proven interaction patterns for behavior, navigation, layout, actions, and data display. Load alongside webapp-gui-design, jetpack-compose-ui, or any frontend skill to produce world-class, non-generic interfaces.
---

# Interaction Design Patterns

Grounded in Tidwell, Brewer & Valencia (2020) *Designing Interfaces*, 3rd ed. — the industry's definitive interaction design pattern library. These patterns describe how real humans behave with software and what interface structures consistently work.

## When to Use

Load this skill alongside any design skill when:
- Choosing a navigation model (Hub and Spoke? Flat? Pyramid?)
- Designing page layouts and information hierarchy
- Planning action flows (undo, preview, cancel, confirmation)
- Displaying complex or interactive data
- Understanding *why* users behave the way they do
- Avoiding AI-generic interfaces by grounding decisions in proven patterns

## Quick Reference

| Category | Key Patterns | Reference |
|----------|-------------|-----------|
| **Behavioral** | Safe Exploration, Instant Gratification, Satisficing, Habituation, Spatial Memory, Prospective Memory | This file |
| **Navigation** | Hub & Spoke, Escape Hatch, Modal Panel, Deep Links, Breadcrumbs, Progress Indicator, Fat Menus | `sections/02-navigation.md` |
| **Layout** | Visual Framework, Center Stage, Grid of Equals, Accordion, Collapsible Panels, Titled Sections | `sections/03-layout.md` |
| **Actions** | Prominent Done Button, Preview, Multi-Level Undo, Hover Tools, Smart Menu Items, Cancelability | `sections/04-actions.md` |
| **Data Display** | Datatips, Data Spotlight, Dynamic Queries, Small Multiples, Multi-Y Graph | `sections/05-data.md` |

---

## 1. Behavioral Design Patterns

These describe how humans naturally interact with software. Design *with* them — not against them.

### Safe Exploration
*"Let me explore without getting lost or getting into trouble."*

Users learn more and feel more positive when they can try things without dire consequences. Exploration is the primary way users discover features. Support it by:
- **Multi-Level Undo** on all reversible actions — unlimited steps, not just one
- **Escape Hatch** always present — a reliable way back to a known-safe state
- **Preview** before committing to irreversible or impactful actions
- Never trapping users in modal flows without an obvious exit
- Back button works predictably on every page — never hijack or break it

**Design rule:** If an action can't be undone, warn explicitly *before* it happens — not after.

---

### Instant Gratification
*"I want to accomplish something now, not later."*

Users must get a success experience within the first few seconds. If they can't, they lose confidence in the product and in themselves.
- Predict the user's first action and make it obviously easy — put it on the first screen
- Never block first use with registrations, tutorials, or long-loading splash screens
- Provide value *before* asking for anything in return (email, payment, sign-up)
- First-time users should complete a meaningful action within 30 seconds

**Design rule:** Every new screen — ask: "What is the ONE thing users do first, and can they see and do it immediately?"

---

### Satisficing
*"This is good enough. I'll stop here."*

Users do not read every element. They scan, pick the first option that might work, and try it. This is rational: parsing a complex interface is cognitive work they'd rather avoid.
- Use **calls to action**: explicit, directive labels — "Start here," "Create invoice," "Upload image"
- Keep all labels **short, plainly worded, and unambiguous** — users guess at meaning before reading
- Use layout, size, and color to communicate importance — these are read before text
- Provide **easy recovery** from wrong choices (Escape Hatch, Undo)
- Visual complexity causes users to pick the first *visible* thing, not the best thing

**Design rule:** If your label requires reading to understand its meaning, rewrite it until a user's first guess is correct.

---

### Changes in Midstream
*"I changed my mind about what I was doing."*

Users change goals mid-task — they start to add an invoice but spot an overdue customer and pivot. Support this gracefully.
- Keep navigation accessible — don't lock users into linear flows without good reason
- Support **reentrance**: half-completed forms save state and resume where the user left off
- Persist draft state: turning off a device or closing a tab should not lose work
- Dialogs and forms should remember previously entered values

**Design rule:** Forcing users to finish a task before doing anything else causes abandonment.

---

### Deferred Choices
*"I don't want to answer that now; just let me finish!"*

Users want to complete their primary task without being interrupted by decisions they don't need to make yet.
- Don't front-load forms with questions the user can't answer or doesn't need to answer now
- Mark **required vs optional** fields clearly — mark optional as "(optional)", not required with asterisks
- Hide long configuration lists behind "Advanced" — show only the short, required list first
- Use **Good Defaults** to pre-answer non-critical decisions (see form-ux-design skill)
- Tell users: "You can always change this later" with a link to where

**Design rule:** Every required question that isn't truly necessary reduces form completion rate.

---

### Incremental Construction
*"Let me change this. That doesn't look right; let me change it again. That's better."*

Builders — writers, designers, coders — work in small iterative cycles. They build a piece, evaluate it, adjust it, and repeat. They don't work in a straight line.
- Support **immediate feedback** after every change — show the result instantly, no wait
- Keep **save and preview cycles fast** — any delay longer than 2 seconds breaks concentration
- Show the state of the whole while the user edits a part (live preview)
- Full Undo/Redo granularity — every small change should be reversible
- Let users have multiple incomplete projects open simultaneously

**Design rule:** Any delay between action and visible result risks breaking the creative flow state.

---

### Habituation
*"That gesture works everywhere else; why doesn't it work here?"*

Frequent actions become reflex. Users stop thinking consciously about common gestures (Ctrl+S, swipe-to-delete, Back button). Breaking habituated patterns causes errors and frustration — especially for expert users.
- Use **universal keyboard shortcuts** exactly as the platform defines them — Ctrl-C, Ctrl-Z, Ctrl-S
- Never reassign a standard gesture or shortcut to a different action, even in a special mode
- Keep **menu items in the same position and order** across all pages and sessions
- Confirmation dialogs are bypassed by habituated OK/Return clicks — don't rely on them for critical protection
- On mobile: verify ALL gestures match the platform's standard behaviour

**Design rule:** Consistency within your app is as important as consistency with the platform. One inconsistent gesture erases expert confidence.

---

### Microbreaks
*"I'm waiting for the train. Let me do something useful for two minutes."*

Users access apps during short windows of available attention — queues, commutes, transitions. Design mobile features for completion in ≤2 minutes.
- App must be fast to start — no setup, no required re-login, no long loading sequences
- Show the **freshest, most relevant content on the first screen** — don't make users navigate to find value
- Support **reentrance**: restore exactly where the user left off, without asking
- Provide efficient triage: show enough data per item to act without opening it

**Design rule:** If your app takes more than 10 seconds from cold launch to primary content, it fails the microbreak test.

---

### Spatial Memory
*"I swear that button was here a minute ago. Where did it go?"*

Users find things by remembering *where* they are, not what they're named. This is powerful and fast — but only if the interface stays stable.
- Keep controls, menus, and navigation items in the **same position** across all pages and sessions
- The **first and last items** in any list are remembered more than the middle — place key items there
- Never "helpfully" rearrange menus based on usage frequency — users rely on position, not recency
- User-arranged layouts support spatial memory — respect user-defined organisation
- Changing navigation items between pages destroys the user's mental map

**Design rule:** Every time you move a UI element, you reset the user's spatial memory for it. Do this only when there's a strong reason.

---

### Prospective Memory
*"I'm putting this here to remind myself to deal with it later."*

Users leave intentional artifacts — open windows, starred items, items on the desktop — as self-made reminder systems. Software must *support*, not clean up, these systems.
- **Never auto-close** idle windows or tabs — they may be intentional reminders
- **Never auto-sort or rearrange** user-placed items unless asked
- Retain **half-finished form state** when the user navigates away and returns
- Provide bookmarking, pinning, starring, and list features for deferred items
- Show "recently visited" and "in-progress" items on return to help users pick up

**Design rule:** When you helpfully clean up after users, you erase their memory system.

---

### Streamlined Repetition
*"I have to do this how many times?"*

Power users often perform the same operation repeatedly. Reducing repetition from 10 clicks to 1 is the quality-of-life win that defines expert-grade tools.
- Provide **bulk/batch operations**: select multiple items, apply action once
- Support **Find and Replace** for repetitive text/value changes
- Enable **Macros**: users record a sequence of actions and replay it with one click
- Design keyboard-only paths for all high-frequency operations
- Offer **clipboard history** beyond just the last item

**Design rule:** Observe your power users for 30 minutes — they will reveal every repetitive task your UI fails to streamline.

---

### Social Proof
*"What did everyone else say about this?"*

People's decisions are shaped by what peers do and say. Social dynamics increase engagement, trust, and conversion.
- Show **user counts, ratings, and reviews** near conversion points
- Display **activity feeds** showing what peers have recently done
- Surface "trending," "popular," or "recommended by others like you" signals
- Build collaboration features: comments, shared views, @mentions

**Design rule:** One genuine peer review outweighs five brand marketing claims.

---

## Integration

```
interaction-design-patterns (this skill)
    |
    +-- webapp-gui-design ------> Apply patterns to Bootstrap/Tabler web UI
    +-- jetpack-compose-ui -----> Apply patterns to Android Compose mobile UI
    +-- ux-psychology ----------> Cognitive science behind the behavioral patterns
    +-- cognitive-ux-framework -> Evaluate patterns against the Six Minds
    +-- form-ux-design ---------> Deferred Choices, Instant Gratification in forms
    +-- lean-ux-validation -----> Validate pattern choices with real users before building
```

---

## Sources

- Tidwell, J., Brewer, C., Valencia, A. (2020). *Designing Interfaces*, 3rd ed. O'Reilly.
- Nielsen, J. (1994). Ten Usability Heuristics. Nielsen Norman Group.
- Krug, S. (2014). *Don't Make Me Think, Revisited.* New Riders.
- Csikszentmihalyi, M. (2009). *Flow: The Psychology of Optimal Experience.* Harper Row.
- Stanford Web Credibility Project (2002). Web Credibility Research. Stanford University.
