# 01 - Behaviour Patterns (Designing for People)

Grounded in Tidwell, Brewer & Valencia (2020) *Designing Interfaces*, 3rd ed., Chapter 1.

These patterns describe how humans actually use software. They shape every other pattern in this skill — pick the right behaviour models first, then the right layout, navigation, action, and data patterns will follow.

Per-pattern format:
- **What** — one-line description.
- **When** — triggers that suggest this pattern applies.
- **Why** — the cognitive or interaction principle.
- **How** — concrete interface affordances.
- **Avoid** — anti-patterns and misapplications.
- **Alternatives** — related patterns for adjacent cases.

---

## Safe Exploration

- **What:** Let users try, back out, undo, and retry without penalty.
- **When:** First-time users, unfamiliar features, complex workflows, anything with branching choices.
- **Why:** Users build a mental model by experimenting. Fear of breakage kills learning and engagement.
- **How:**
  - Provide Undo and Redo; keep a history of actions.
  - Allow cancel at any step in multi-step flows.
  - Use reversible defaults; irreversible actions get friction (confirmation, typed keyword).
  - Treat the Back button as sacred — it must restore prior state.
  - Preview changes before commit (live preview, draft mode).
- **Avoid:** Modal dead-ends, destructive actions without warning, state losses on navigation.
- **Alternatives:** Multi-Level Undo, Cancelability, Preview (all in `04-actions.md`).

## Instant Gratification

- **What:** Reward the user within seconds of arrival with something useful.
- **When:** Onboarding, landing pages, new-user first session, any acquisition-sensitive surface.
- **Why:** Users decide if an app is worth their time in the first few interactions. Fast reward creates engagement; slow reveal kills intent.
- **How:**
  - Ship value in the empty state (sample content, quick templates, one-click setup).
  - Defer signup and permissions — let users taste before committing.
  - Make the first screen a clear "do X now" rather than a tour.
  - Show progress toward value visually.
- **Avoid:** 6-step onboarding wizards before anything useful, mandatory signup wall, tutorial videos forced pre-use.
- **Alternatives:** Progressive Disclosure, Deferred Choices.

## Satisficing

- **What:** Users pick the first acceptable option, not the best option. They scan, they don't analyse.
- **When:** Every list, menu, search result, dropdown, form field, and decision screen.
- **Why:** Krug's "Don't Make Me Think" — cognitive effort is expensive. Users satisfice for speed.
- **How:**
  - Order items by likelihood, not alphabet (unless the user knows the exact name).
  - Highlight recommended defaults.
  - Show plenty of visual noise-reduction: whitespace, typographic hierarchy.
  - Labels should make the right choice obvious.
  - Avoid "analysis paralysis" — cap options at 7 in visible menus (Miller's Law).
- **Avoid:** Long alphabetical dropdowns, unclear default choices, heavy text descriptions that slow scanning.
- **Alternatives:** Good Defaults, Recommended (in forms), Smart Menu Items.

## Changes in Midstream

- **What:** Users change their goal mid-task. The interface must adapt without forcing restart.
- **When:** Long wizards, checkout, multi-screen flows, any sequential task of more than 3 steps.
- **Why:** Real tasks branch and revise; linear wizards assume a static goal.
- **How:**
  - Allow edit-in-place on earlier steps without losing later data.
  - Display progress with all steps visible and clickable.
  - Save partial state automatically so abandoned flows resume later.
  - Offer "skip this step" or "come back later" for optional steps.
- **Avoid:** One-way wizards, lost state on back-nav, forcing completion order when not truly required.
- **Alternatives:** Deep-linked State, Wizard with Step Editor (in `02-navigation.md`).

## Deferred Choices

- **What:** Let users postpone decisions they are not yet ready to make.
- **When:** Onboarding, account setup, configuration, long forms, any moment of uncertainty.
- **Why:** Forcing decisions under incomplete context causes abandonment or wrong choices that must later be fixed.
- **How:**
  - "Do this later" or "Skip for now" buttons with a gentle nudge to return.
  - Save drafts; let users complete work asynchronously.
  - Default placeholder values (e.g. "Untitled Project") that can be edited later.
  - Surface deferred items as reminders.
- **Avoid:** Mandatory fields that demand trivial answers up-front, blocking CTAs that refuse defaults.
- **Alternatives:** Good Defaults, Drafts, Progressive Signup.

## Incremental Construction

- **What:** Users build artefacts in small iterative steps, reviewing often.
- **When:** Documents, spreadsheets, designs, code, forms, configurations — anything the user authors.
- **Why:** Humans think by making, not planning. They need fast feedback loops.
- **How:**
  - Live preview / autosave / instant render.
  - Granular undo at the step level, not per save.
  - Branching history (document versions, design variants).
  - Zero-friction iteration: one-click duplicate, one-click rename, one-click revert.
- **Avoid:** Save-only commit model for authoring tools; batched re-compilation between changes.
- **Alternatives:** Preview, Multi-Level Undo, Versioning.

## Habituation

- **What:** Frequent users build muscle memory. Changing familiar affordances breaks them.
- **When:** Product redesigns, feature updates, power-user flows, keyboard shortcuts, toolbar placement.
- **Why:** Habituated actions are fast and accurate; relearning erases productivity and angers loyal users.
- **How:**
  - Keep high-frequency controls in stable locations across releases.
  - Preserve keyboard shortcuts across updates; add new ones rather than remaps.
  - Provide migration toggles ("use old layout") during big redesigns.
  - Warn users in advance when a habit-forming element will move.
- **Avoid:** Reshuffling menus in minor releases; changing keyboard shortcuts without a preference toggle.
- **Alternatives:** Keyboard Only, Spatial Memory.

## Microbreaks

- **What:** Users fit app-use into very short windows (30-90 seconds) between other tasks.
- **When:** Mobile feeds, quick utilities, notifications, inbox zero flows, bite-sized media.
- **Why:** Mobile context especially is attention-fragmented. If a session requires more than a minute of focus to produce value, it loses.
- **How:**
  - Support one-hand, thumb-zone interaction on mobile.
  - Make save/resume transparent — user drops the app mid-sentence and returns without loss.
  - Surface the most common short-session action first.
  - Provide glanceable summaries on the home screen (counts, badges, digests).
- **Avoid:** Deep flows on mobile, modal dialogs that trap attention, forcing focus for non-critical tasks.
- **Alternatives:** Deferred Choices, Spatial Memory (for return users), Progress Indicator.

## Spatial Memory

- **What:** Users remember where things are on-screen, not what they are called.
- **When:** Toolbars, menus, maps, dashboards, document outlines, any visually consistent interface.
- **Why:** The brain stores location faster than label. Rearranging UI destroys this memory.
- **How:**
  - Keep toolbar button positions stable across sessions, even on context changes.
  - Respect user-arranged layouts (sidebars, pinned items).
  - Consistent icon placement across similar screens.
  - Avoid adaptive menus that re-order based on usage; they destroy spatial memory.
- **Avoid:** Most-recently-used toolbars, random insertion of new items, ribbon reorganisation between versions.
- **Alternatives:** Habituation, Stable Navigation.

## Prospective Memory

- **What:** Users remember to do something later, and the app can help them remember.
- **When:** Follow-ups, scheduled tasks, commitments, drafts, partially-complete actions.
- **Why:** Humans are bad at remembering future intentions; an interface that supports this reduces friction and anxiety.
- **How:**
  - Allow "remind me later" on any item.
  - Surface drafts, saved items, in-progress work prominently.
  - Expose unfinished tasks in the home/dashboard.
  - Integrate with calendars and notifications for deferred actions.
- **Avoid:** Hidden drafts folder, commitments that expire silently, no way to mark "I'll deal with this later".
- **Alternatives:** Deferred Choices, Drafts, Reminders.

## Streamlined Repetition

- **What:** Repetitive actions get shortcuts — macro recording, bulk selection, keyboard actions, templates.
- **When:** Any workflow where the same action runs many times: data entry, email triage, code editing, bulk file operations.
- **Why:** Repetition magnifies small inefficiencies into frustration and errors.
- **How:**
  - Bulk select + bulk action on lists.
  - Keyboard shortcuts for primary actions.
  - Templates, snippets, saved searches.
  - Macro / record-a-sequence (for complex tools).
  - "Apply to all" or "repeat for next" on modal dialogs.
- **Avoid:** One-at-a-time action loops, no bulk, no keyboard path for frequent operations.
- **Alternatives:** Macros, Command History (in `04-actions.md`).

## Keyboard Only

- **What:** Every action reachable from the keyboard, in a logical tab order, with visible focus.
- **When:** Always, for accessibility; and especially for power-user tools (IDEs, email, spreadsheets, command palettes).
- **Why:** WCAG 2.1 requires it. Power users are faster with keyboard. Assistive technology depends on it.
- **How:**
  - Tab order follows reading order; Shift+Tab reverses.
  - Visible focus ring on all interactive elements (never `outline: none`).
  - Shortcuts documented and discoverable (Cmd+K command palette, ? for help).
  - Escape cancels modals; Enter submits forms; arrows navigate lists.
  - No mouse-only gestures (hover menus that hide on blur, drag-only reorders).
- **Avoid:** Mouse-exclusive drag-and-drop, invisible focus, custom widgets that trap focus.
- **Alternatives:** Screen-reader compatibility patterns (not covered here — see `ux-principles-101`).

## Other People's Advice

- **What:** Users trust peer recommendations more than marketing. Surface what similar users do.
- **When:** Onboarding, product pages, empty states, decision screens ("choose a plan"), social apps.
- **Why:** Social proof and expert endorsement reduce decision anxiety.
- **How:**
  - Show counts ("2.3M users use this feature"), ratings, reviews.
  - Peer recommendations ("people like you also chose...").
  - Expert quotes or testimonials placed near decision points.
  - Aggregate activity streams ("12 people viewing this now").
- **Avoid:** Fake social proof, forced testimonials, dark patterns pressuring decisions.
- **Alternatives:** Personal Recommendations, Editorial Mix (see `07-social.md`).

## Personal Recommendations

- **What:** Personalised suggestions based on the user's own history and preferences.
- **When:** Content platforms, shopping, search, media, education — any place with a catalogue.
- **Why:** Relevance converts; generic lists get scrolled past.
- **How:**
  - "Because you read X" / "Based on your history" explainers accompany each recommendation.
  - Allow explicit feedback: thumbs up/down, "not interested", "more like this".
  - Respect privacy expectations — let users see and edit what drives the recommendations.
  - Mix recommendations with editorial and random discovery to avoid filter bubbles.
- **Avoid:** Recommendations without explanation, impossible-to-correct filter bubbles, creepy signals.
- **Alternatives:** Editorial Mix, Collaborative Filtering (systems-level, not UI).

---

## Behaviour-to-Pattern Map (Quick Reference)

When a behavioural trigger appears, consider these interface patterns:

| Behaviour | First-line patterns (from other sections) |
|---|---|
| Safe Exploration | Multi-Level Undo, Cancelability, Preview, Escape Hatch |
| Instant Gratification | Good Defaults, Fill-in-the-Blanks, Sample Content, Progress Indicator |
| Satisficing | Good Defaults, Dropdown Chooser, Sorted Lists, Smart Menu Items |
| Changes in Midstream | Progress Indicator, Deep-linked State, Deferred Choices |
| Deferred Choices | Drafts, "Later" buttons, Placeholder Names |
| Incremental Construction | Preview, Autosave, Multi-Level Undo |
| Habituation | Stable Nav, Consistent Toolbar, Preserve Keyboard Shortcuts |
| Microbreaks | Bottom Navigation, Glanceable Summary, Autosave |
| Spatial Memory | Stable Toolbar, Avoid Adaptive Menus, Movable Panels (with persistence) |
| Prospective Memory | Drafts tray, Reminders, "Pinned" items |
| Streamlined Repetition | Bulk Selection, Macros, Command History, Keyboard Shortcuts |
| Keyboard Only | Visible focus, Tab order, Shortcuts, Command palette |
| Other People's Advice | Social Proof counts, Testimonials, Leaderboard |
| Personal Recommendations | Because-you... explainers, Feedback controls |

---

## Companion Patterns

These behaviours flow into the patterns in:

- `02-navigation.md` — signposting, wayfinding, escape hatches.
- `03-layout.md` — page structure that supports scanning and satisficing.
- `04-actions.md` — reversibility, command patterns, undo, shortcuts.
- `05-data.md` — lists and data displays that respect cognitive limits.
- `ux-psychology` skill — deeper cognitive foundations.
- `laws-of-ux` skill — named laws (Miller, Hick, Fitts, Jakob).
- `habit-forming-products` skill — repeat engagement design.
