# Navigation Patterns

From Tidwell, *Designing Interfaces*, 3rd ed., Chapter 3: Getting Around — Navigation, Signposts, and Wayfinding.

> "The best kind of commuting is none at all." — Tidwell. Keep navigation distances short. Every extra click is friction.

---

## Navigation Models

Choose one model before designing the navigation structure. These are architectural decisions — not visual ones.

| Model | Structure | Best For |
|-------|-----------|----------|
| **Hub and Spoke** | Central home → separate workspaces | Mobile apps, wizard flows, dedicated task areas |
| **Fully Connected** | Every section reachable from every other | Small sites, apps where cross-navigation is common |
| **Multilevel / Tree** | Hierarchical parent → child sections | Large content sites, enterprise apps with many modules |
| **Step-by-Step** | Linear A → B → C with no branching | Checkout flows, registration wizards, onboarding |
| **Flat Navigation** | 3–5 top-level sections, no nesting | Simple apps, mobile apps, tools with few distinct areas |
| **Pyramid** | Home → category → item → detail | E-commerce, document libraries, content sites |

**Decision rule:** If a user needs to jump between unrelated areas frequently → Fully Connected. If areas are self-contained tasks → Hub and Spoke. If content is deeply categorised → Tree. If you're onboarding → Step-by-Step.

---

## Wayfinding Principles

Users navigate like people navigating a building — they look for signposts, environmental clues, and maps.

**Good signage:** Labels at every decision point that clearly predict their destination. Weak information scent ("Data" instead of "Order History") causes users to abandon paths.

**Environmental clues:** Logos top-left, close button top-right, user avatar top-right — these are learned conventions. Breaking them forces users to stop and re-orient.

**Maps:** Progress indicators, breadcrumbs, and site maps help users build a mental picture of where they are in the whole.

**Cognitive cost of navigation:** Every page transition incurs a reorientation cost. Design to minimise the number of transitions to complete any task.

---

## Navigation Patterns

### Clear Entry Points
*"Show me where to start."*

The starting screen must make the user's first action immediately obvious. One prominent CTA, not six equal-weight options.
- One dominant visual entry point per starting screen
- Supporting entry points clearly secondary (smaller, less prominent)
- Labels that describe the outcome: "Create your first invoice" not "Get Started"
- For returning users: show where they left off (recent items, in-progress work)

**Anti-pattern:** Five equally sized cards/buttons on the home screen — users freeze or satisfice on the wrong one.

---

### Modal Panel
*"Focus on this one thing, then return."*

A modal panel requires the user to complete or dismiss it before returning to the main interface. Use only when you genuinely need exclusive focus.
- Use for: confirmations, critical data entry, previews, focused sub-tasks
- Always provide a clear, obvious close/cancel control (top-right X, ESC key, Cancel button)
- Never use for content the user might need to reference while the modal is open
- Modal should not cover the entire screen on desktop — leave context visible around it
- Keyboard: ESC always dismisses; Tab cycles through controls inside the modal

**Anti-pattern:** Using a modal for information display. If the user needs to read it and continue, use an inline message or toast instead.

---

### Escape Hatch
*"Get me out of here — take me somewhere familiar."*

No matter where a user is in your application, they must always have a way back to a known-safe, familiar place.
- Every page has a link to Home or Dashboard
- Breadcrumbs provide intermediate escape points
- The browser Back button must work predictably on every page
- Wizard flows have a visible Cancel option that returns to the previous state
- Deep modal chains have a visible way to collapse all the way back to the start

**Design rule:** If the user clicks Back and nothing happens — or something unexpected happens — your Escape Hatch is broken.

---

### Deep Links
*"Let me share this exact page with someone."*

Every meaningful view in an application should have a stable, shareable URL or identifier. Users share links in emails, Slack, and bookmarks. If the URL changes on every load, this is impossible.
- Use meaningful, human-readable URL structures (not UUIDs as slugs)
- Dashboard filters, search queries, and table sorts should be reflected in the URL
- Shareable links should restore the full view state — not just the page
- Authenticated pages require the recipient to log in first, then redirect to the intended page

---

### Fat Menus
*"I want to see all my options before choosing."*

Mega-menus show a large panel of navigation options on hover/click, replacing a standard dropdown. Use for sites with many sections that users need to browse.
- Organise options into logical groups with section headers
- Show 10–30 options maximum — more than that and users stop reading
- Include brief descriptions or icons for each option to strengthen information scent
- Highlight the most-used or most-important options visually
- Keep consistent with the rest of the navigation — mega-menus should not feel like a different product

**When NOT to use:** Apps with fewer than 7 total sections, or anywhere mobile is the primary interface (fat menus are touch-hostile).

---

### Breadcrumbs
*"Show me where I am in the hierarchy."*

Breadcrumbs show the user's current location as a path: Home > Sales > Invoices > Invoice #1042.
- Required for hierarchies deeper than 2 levels
- Every breadcrumb segment except the last is a clickable link
- The last segment (current page) is plain text — not a link
- Use a separator character consistently: › or / or >
- Place at the top of the page content, below the main navigation
- Breadcrumbs show hierarchy, not history — they reflect the IA structure, not the user's click path

**Anti-pattern:** Breadcrumbs that show the browser history instead of the content hierarchy. These confuse users about the app's structure.

---

### Progress Indicator
*"How many more steps do I have?"*

For any multi-step process (wizard, checkout, onboarding), show the user where they are and how far they have to go.
- Show step number and label: "Step 2 of 4: Payment"
- Mark completed steps with a visual indicator (checkmark, filled circle, different colour)
- Mark the current step as active
- Show future steps as pending (greyed out, hollow circle)
- Never show a percentage for wizard steps — "Step 2 of 4" is clearer than "50% complete"
- Place at the top of the step content, not in the sidebar

**Anti-pattern:** Showing 12+ steps in a progress indicator. Users see the total number and feel the process is too long. Break into phases (Phase 1, Phase 2) if more than 6 steps are needed.

---

### Annotated Scroll Bar
*"Show me where the interesting content is in this long page."*

Annotated scroll bars place markers on the scroll track to indicate where relevant content is located — headings, search matches, errors, bookmarks.
- Use when content is very long (2000+ px) and users need to jump to specific sections
- Place heading markers for navigation-heavy documents
- Highlight search result positions on the scroll track
- Mark error locations in long forms — jump to first error on submit

---

### Animated Transition
*"Help me understand what just changed."*

When the view changes — page loads, panel opens, modal appears — a brief, purposeful animation helps the user understand the spatial relationship between old and new states.
- Use for: modals sliding up from bottom, panels expanding, page transitions between list and detail
- Duration: 150–300ms. Anything longer feels sluggish.
- Use easing (ease-in-out or deceleration) — never linear
- Transition should reinforce the navigation model (sliding right = going deeper; sliding left = going back)
- Never animate on page load delays — animation should not mask slow performance

**Anti-pattern:** Decorative transitions that serve no navigational purpose. If you can't explain what the animation communicates about spatial position, remove it.

---

## Navigation Anti-Patterns

| Anti-Pattern | Why it Fails |
|-------------|-------------|
| No visible current location indicator | Users don't know where they are — they can't navigate efficiently |
| Navigation items that move between pages | Destroys spatial memory — users have to re-locate controls constantly |
| Hiding navigation in hamburger menus on desktop | Navigation that requires a click to reveal is navigation users won't use |
| Using icons without labels in primary navigation | Icons alone are not universally understood — always pair with text on desktop |
| Links that open in new tabs without warning | Users lose their navigation context and can't use Back |
| Modal dialogs that block the user with no escape | Creates anxiety; users who feel trapped will abandon the task |
| Deep nesting > 3 levels without breadcrumbs | Users lose their place and abandon exploration |
