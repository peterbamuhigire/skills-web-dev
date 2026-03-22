# Action and Command Patterns

From Tidwell, *Designing Interfaces*, 3rd ed., Chapter 8: Doing Things — Actions and Commands.

> "Affordance means that it looks or behaves like what it does. A button that looks slightly three-dimensional gives a visual cue that it is clickable." — Tidwell.

---

## Action Mechanisms — Choosing the Right One

| Mechanism | Best For | Notes |
|-----------|---------|-------|
| **Button** | Primary actions, CTAs, destructive actions | Large, obvious, always visible |
| **Link (text)** | Navigation, secondary/inline actions | Blue text = clickable is universally understood |
| **Icon button** | Toolbars, repeated compact actions | Must be universally understood icons; label on hover |
| **Hover/Pop-Up Tools** | Item-level actions on lists/tables | Reduces clutter; show on hover |
| **Context menu (right-click)** | Power user actions on objects | Supplemental — never the only way to reach an action |
| **Action Panel** | Persistent set of related actions on a complex screen | Always visible, verbally described |
| **Toolbar** | Frequently used visual editing actions | Icon-first; best when actions have obvious visual representations |
| **Keyboard shortcut** | High-frequency actions for expert users | Always supplement — never the only path |
| **Drag and drop** | "Move this here" / "Do this to that" | Support as enhancement; ensure keyboard/click alternatives exist |

**Design rule:** An action buried in a right-click context menu will not be discovered by most users. Visible actions teach; hidden actions don't.

---

## Action Patterns

### Button Groups
*"These actions belong together — show them together."*

Related actions should be grouped visually and physically. Users learn that "actions appear in this area" and look there reliably.
- Group by relationship: primary + secondary + destructive, or a set of filter options
- Visual grouping: adjacent placement, border around the group, or a subtle separator between groups
- Primary action: filled/solid button. Secondary: outlined. Destructive: red or ghost with red hover.
- Separate the destructive action from the safe ones — physical distance prevents accidental clicks
- Maximum 4–5 buttons in a group before using a dropdown or action panel

---

### Hover / Pop-Up Tools
*"Show me tools only when I'm looking at this item."*

For lists and tables where each row has actionable operations, hovering over the row reveals contextual action buttons. This keeps the interface clean when users are scanning and provides tools when they're ready to act.
- Show Edit, View, Delete icons on row hover — not permanently rendered on every row
- Transition in: fade or slide, 100–150ms
- On touch screens (mobile): never use hover tools — show actions in a tap-to-reveal overflow menu or swipe action
- Ensure keyboard users can also access these actions (focus + keyboard shortcut, or focus reveals the tools)
- Always ensure the actions are also discoverable via a context menu or action panel

---

### Action Panel
*"Here are all the things I can do from this screen."*

An action panel is a persistent, always-visible set of actions relevant to the current context. Unlike a toolbar (icons), an action panel uses text labels — useful when actions require words to be understood.
- Position: sidebar panel, card footer, or dedicated action column
- Show only actions relevant to the current context — filter by state (e.g., "Approve" only shows for pending items)
- Organise into logical groups if more than 5 actions
- Primary action is the most prominent. Destructive action is last, visually separated.
- Use an action panel when actions are complex enough to require labels, not just icons

---

### Prominent Done Button
*"Make the primary action unmistakably obvious."*

Every screen or modal has one primary action — the thing the user is most likely to want to do next. It must stand out visually and be easy to reach.
- One primary button per context (form, modal, page section). Always filled/solid.
- Placed where the user's eye lands after reading the content — typically bottom-right of a form or modal, or top-right of a page header
- Label is the action: "Save", "Submit", "Create Invoice", "Send Message" — not generic "OK" or "Submit"
- Keyboard: Enter or Ctrl+Enter should trigger the primary button in forms
- The button should be enabled throughout — never disable it hoping users will figure out what's wrong. If there are validation errors, show them on submit.

**Anti-pattern:** Three equally weighted buttons side by side — users don't know which one to click. One must clearly be primary.

---

### Smart Menu Items
*"The menu item tells me exactly what will happen."*

Menu items and button labels that include contextual specifics are far more informative than generic labels. "Undo Delete Customer: Acme Corp" tells the user exactly what Undo will reverse. "Undo" does not.
- Use the object name in the label: "Delete Invoice #1042" not just "Delete"
- Undo should name what it undoes: "Undo Rename" not "Undo"
- For batch operations: "Delete 3 Selected Items" not "Delete"
- Disabled menu items: explain why they're disabled — "Can't delete: invoice has payments" — or hide them entirely

---

### Preview
*"Show me what will happen before I commit."*

For actions that have a significant visible result — applying a template, sending a message, generating a report — show the user what the outcome will look like before they confirm.
- "Preview" button or panel shows the result in real time or on-demand
- For document generation (PDF, email, report): render a preview in a modal before final confirmation
- For settings changes: live preview in a side panel while settings are edited
- For destructive actions: show a summary of what will be affected ("You are about to delete 3 invoices totalling $4,200")
- Preview reduces confirmation anxiety and the rate of mistakes

---

### Cancelability
*"Let me stop this before it's too late."*

Any operation that takes more than 1–2 seconds should be cancellable. Any long-running operation must be cancellable. This is non-negotiable for trust.
- Show a Cancel button immediately when a progress indicator appears
- Cancel actually stops the operation — it doesn't just close the progress indicator
- If cancellation isn't possible partway through (database transaction, external API), say so upfront — not after the user clicks Cancel
- File uploads, imports, bulk operations, and long calculations all require Cancel
- Email/message sending: provide a brief "Undo Send" window (5–10 seconds) before the message is actually dispatched

---

### Multi-Level Undo
*"Let me go back more than one step."*

A single Undo is the minimum. Users doing creative or iterative work need to undo multiple steps — sometimes 20+ steps back.
- Support unlimited undo steps (or a practical maximum of 50+)
- Undo is Ctrl+Z / Cmd+Z — this is an absolute universal convention; never override it
- Redo is Ctrl+Shift+Z or Ctrl+Y — equally universal
- Show the undo history when users hold the undo button (list of recent actions)
- Smart Menu Item: "Undo Delete Customer" tells the user what they're undoing
- Never lose undo history on save — saving should not empty the undo stack

**Design rule:** Every time a user can't undo an action, they feel less safe exploring your interface.

---

### Command History
*"Show me what I've done in this session."*

For power tools (data entry, document editing, configuration), expose the list of recent actions so users can review, repeat, or reverse them.
- Show the history as a scannable list: action + timestamp + object affected
- Allow users to click a history item to jump to that state (combined with Multi-Level Undo)
- Useful for: audit trails, troubleshooting, learning shortcuts from watching one's own behaviour
- Separate from Undo history — Command History is informational; Undo is functional

---

### Macros
*"Let me record this sequence and replay it."*

When users perform the same multi-step sequence repeatedly, give them a way to record it and replay it with a single click.
- A "Record" mode captures all user actions as a named sequence
- Playback executes the sequence on the current selection or context
- Simple macro systems: "Find and Replace All", "Apply this filter preset", "Duplicate with these defaults"
- Advanced: scripted macros for power users (Photoshop Actions, Excel Macros model)
- Even simple one-level macros (saved filter sets, saved search queries) have high value for repetitive workflows

---

## Keyboard and Accessibility

Every action reachable by mouse must also be reachable by keyboard. This is a requirement — not optional.

| Keyboard convention | Action |
|--------------------|--------|
| **Tab / Shift+Tab** | Move focus between controls |
| **Enter / Space** | Activate focused button or checkbox |
| **Escape** | Close modal, cancel dialog, cancel hover tool |
| **Arrow keys** | Navigate within lists, menus, and radio groups |
| **Ctrl+Z / Cmd+Z** | Undo |
| **Ctrl+S / Cmd+S** | Save |
| **Ctrl+K / Cmd+K** | Global search (modern convention) |
| **Ctrl+Enter** | Submit form / send message |

**Tab order** should follow the visual reading order of the page (top-left to bottom-right). A logical tab order is required for screen reader users and keyboard-only users.

---

## Action Anti-Patterns

| Anti-Pattern | Why it Fails |
|-------------|-------------|
| No Undo for destructive actions | Users avoid doing things they can't reverse — reduces engagement |
| Generic button labels ("Submit", "OK", "Yes") | Users don't know what will happen until after they click |
| Irreversible actions with no confirmation | Creates anxiety; users make mistakes they can't recover from |
| Cancel that doesn't actually cancel | Destroys trust — "Cancel" must cancel, not just close the dialog |
| Long operations with no progress and no Cancel | Users assume the app is broken; they force-quit |
| Primary action the same visual weight as secondary | Users don't know what to do next |
| Hover-only actions on touch interfaces | Touch users can't hover — those actions are invisible to them |
| Double-click as the only way to open an item | Not discoverable; breaks keyboard-only access |
