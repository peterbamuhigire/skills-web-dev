---
name: ux-writing
description: "Microcopy and UX writing standards for buttons, error messages, empty states, loading states, form labels, confirmations, tooltips, and onboarding. Covers voice vs tone, accessibility in writing, translation readiness, and consistency rules. Cross-platform (web, Android, iOS). Based on Impeccable (Bakaus, 2025)."
---

# UX Writing Skill

## Plugins (Load Alongside)

| Companion Skill | When to Load |
|---|---|
| `practical-ui-design` | Visual system for text styling |
| `form-ux-design` | Deep form label and validation patterns |
| `content-writing` | Long-form copywriting (articles, blogs) |
| `language-standards` | Multi-language standards (EN/FR/SW) |
| `ai-slop-prevention` | Catch generic AI copy patterns |

**Scope:** This skill covers **interface microcopy** — the short text inside apps. For long-form content (articles, blogs, marketing pages), use `content-writing` instead.

---

## 1. Core Principles

| Principle | Meaning |
|---|---|
| **Specific** | Say exactly what happened, what to do, what it means |
| **Concise** | If a word can be removed without losing meaning, remove it |
| **Active** | Use active voice ("We saved your file" not "Your file has been saved") |
| **Human** | Write as a helpful colleague, not a robot or a lawyer |
| **Helpful** | Every piece of text should help the user take their next step |
| **Consistent** | Same term for the same concept everywhere in the product |

---

## 2. Button Labels

### The Formula: Verb + Noun

| BAD | GOOD | Why |
|---|---|---|
| Submit | Create account | Specific action + object |
| OK | Save changes | Names the consequence |
| Yes / No | Delete message / Keep message | Names both outcomes |
| Click here | View pricing plans | Describes destination |
| Cancel | Discard draft | Says what actually happens |
| Confirm | Place order | Matches user's mental model |

### Rules

- **Primary button**: always verb + noun ("Save changes", "Send invitation")
- **Cancel/dismiss**: name what happens ("Discard changes", "Keep editing", "Go back")
- **Destructive actions**: name the destruction ("Delete account", "Remove member")
- **Never use "Submit"** — it says nothing about what the user is submitting
- **Never use "OK"** — it's ambiguous in every context
- Sentence case for all button text

---

## 3. Error Messages

### The Three-Part Formula

Every error message must answer:

1. **What happened?** — State the problem clearly
2. **Why?** — Explain the cause (if helpful)
3. **How to fix it?** — Give a specific action

### Examples

| BAD | GOOD |
|---|---|
| Error | Your password must be at least 8 characters |
| Invalid input | Enter a valid email address (e.g., name@example.com) |
| Something went wrong | We couldn't save your changes. Check your connection and try again. |
| 404 | We can't find that page. It may have been moved or deleted. |
| Request failed | The file is too large. Choose a file under 10 MB. |
| Validation error | Enter a date after today |

### Rules

- **Never blame the user**: "Invalid input" → "Enter a date in DD/MM/YYYY format"
- **Never use error codes alone**: "Error 5012" → translate to plain language
- **Never use "Something went wrong"** — always be more specific
- **Never use humour in error messages** — users are frustrated, not amused
- Show errors **inline near the problem**, not in a distant toast
- Use red styling + icon (never colour alone)

---

## 4. Empty States

Empty states are **onboarding moments**, not dead ends.

### The Three-Part Formula

1. **Acknowledge**: "No invoices yet" (state what's empty)
2. **Explain value**: "Create invoices to track payments from your clients" (why they should care)
3. **Provide action**: [Create your first invoice] button (clear next step)

### Examples

| BAD | GOOD |
|---|---|
| No data | No projects yet. Create a project to start tracking your work. [New project] |
| Nothing to show | Your inbox is empty. Messages from your team will appear here. |
| No results | No matches for "flibbertigibbet". Try different keywords or check the spelling. |
| (blank screen) | You haven't added any team members yet. Invite your team to start collaborating. [Invite team] |

### Rules

- Never leave a blank screen — always show an empty state
- Use an illustration or icon to add warmth (avoid generic stock illustrations)
- The action button should be the same as the normal "create" action
- Search empty states: suggest corrections, related results, or broader filters

---

## 5. Loading States

### Be Specific

| BAD | GOOD |
|---|---|
| Loading... | Saving your draft... |
| Please wait | Generating your report... |
| Processing | Uploading 3 of 12 photos... |
| One moment | Connecting to payment provider... |

### Rules

- Name the operation: "Saving", "Uploading", "Sending", "Generating"
- Show progress when possible: "Uploading 3 of 12 photos (24%)"
- For operations < 80ms: skip the loading state entirely
- For operations < 2s: use a subtle inline indicator (not a full-screen overlay)
- For operations > 4s: add estimated time remaining or context
- Never use humorous loading messages ("Reticulating splines") — they wear thin fast

---

## 6. Success Messages

### Be Specific and Brief

| BAD | GOOD |
|---|---|
| Success! | Invoice #1042 sent to client@example.com |
| Done | Your changes have been saved |
| Completed | Payment of UGX 500,000 processed |

### Rules

- Name what succeeded and include relevant details (name, email, amount)
- Show as a non-blocking toast or inline confirmation (not a modal)
- Auto-dismiss after 5-8 seconds
- Include an undo action where reversible: "Message deleted. [Undo]"
- Don't celebrate routine actions — save celebration for milestones

---

## 7. Confirmation Dialogs

### Use Sparingly

Most actions should be undoable, eliminating the need for confirmation.

### When Required

- **Irreversible destructive actions** (delete account, remove data)
- **Actions with significant consequences** (send to 10,000 recipients)
- **Actions that cost money** (place order, process payment)

### Structure

```
[Heading]: Name the action ("Delete this project?")
[Body]: State the consequence ("All 47 tasks and files will be permanently deleted.")
[Primary]: Name the action ("Delete project") — use red for destructive
[Secondary]: Name the safe option ("Keep project")
```

### Rules

- Never use "Are you sure?" — name the action instead
- Never use "Yes" / "No" — name both outcomes
- Primary button should match the dialog heading verb
- Destructive primary buttons use red/danger styling

---

## 8. Form Labels and Help Text

### Labels

- Always visible (never placeholder-as-label)
- Short and specific: "Email address" not "Please enter your email address"
- Drop "My" / "Your": use "Email" not "Your email"
- Sentence case

### Help Text (Hints)

- Place **above** the field (below gets covered by autofill/keyboard on mobile)
- Explain format or constraints: "Must be at least 8 characters with one number"
- Use for non-obvious requirements only — don't explain "First name"

### Placeholder Text

- Use for **examples only**: `e.g., name@example.com`
- Never as the label (disappears on input)
- Never as help text (disappears on input)
- Use lighter colour (but note: placeholder text often fails contrast requirements)

---

## 9. Voice vs Tone

### Voice (Consistent)

Your product's personality — stays the same everywhere. Define once:

- **Professional but approachable** (not stiff, not casual)
- **Clear and direct** (not verbose, not cryptic)
- **Helpful and confident** (not apologetic, not arrogant)

### Tone (Adapts to Moment)

| Moment | Tone | Example |
|---|---|---|
| Onboarding | Warm, encouraging | "Welcome! Let's set up your workspace." |
| Success | Brief, satisfied | "Payment processed." |
| Error | Calm, helpful | "We couldn't connect. Check your internet and try again." |
| Destructive action | Serious, clear | "This will permanently delete all project data." |
| Empty state | Optimistic, guiding | "No messages yet. Start a conversation with your team." |
| Waiting | Reassuring | "Generating your report. This usually takes 10-15 seconds." |

---

## 10. Accessibility in Writing

### Link Text

- Must make sense **out of context** (screen readers list links separately)
- BAD: "Click here", "Read more", "Learn more"
- GOOD: "View pricing plans", "Read the API documentation"

### Alt Text

- **Informational images**: describe the information ("Bar chart showing sales up 23% in Q4")
- **Decorative images**: empty alt (`alt=""`)
- **Functional images** (icons as buttons): describe the function ("Close dialog", "Search")

### ARIA Labels

- Icon-only buttons MUST have `aria-label`: `<button aria-label="Close dialog">✕</button>`
- Use `aria-describedby` to connect help text to form fields
- Use `aria-live="polite"` for dynamic status messages

---

## 11. Translation Readiness

### Plan for Text Expansion

| Language | Expansion vs English |
|---|---|
| German | +30-35% |
| French | +15-20% |
| Finnish | +30-40% |
| Chinese/Japanese/Korean | -10-30% (but may need taller line height) |
| Arabic/Hebrew | RTL layout + similar length |

### Rules

- Design UI to accommodate 40% longer text
- Never hard-code string widths
- Keep numbers, dates, and currencies as separate tokens (not embedded in strings)
- Avoid idioms, puns, and cultural references that don't translate
- Use ICU MessageFormat for plurals (not `item(s)`)
- Test with pseudo-localisation (replace characters with extended versions)

---

## 12. Consistency Rules

- **One term per concept**: if you use "Delete", don't also use "Remove" for the same action
- **One pattern per interaction**: if lists use swipe-to-delete, all lists should
- **Document your vocabulary**: maintain a terminology glossary
- Common pairs to standardise:

| Pick ONE | Don't Mix |
|---|---|
| Delete | Remove, Trash, Discard |
| Edit | Modify, Change, Update |
| Create | Add, New, Make |
| Settings | Preferences, Options, Configuration |
| Sign in | Log in, Login |

---

## 13. Quality Checklist

- [ ] All buttons use verb + noun (no "Submit", "OK", "Yes/No")
- [ ] Error messages explain what, why, and how to fix
- [ ] Empty states provide context + action
- [ ] Loading states name the operation
- [ ] Confirmation dialogs name both action and safe option
- [ ] Link text makes sense out of context
- [ ] Vocabulary is consistent (same term = same concept)
- [ ] Tone matches the moment (serious for errors, warm for onboarding)
- [ ] No AI slop vocabulary ("leverage", "robust", "seamlessly", "delve")
- [ ] Text expansion tested for i18n (40% buffer)
- [ ] Icon-only buttons have aria-label

---

*Sources: Impeccable ux-writing reference (Bakaus, 2025); microcopy patterns from UX Writing Hub; Nielsen Norman Group error message guidelines.*
