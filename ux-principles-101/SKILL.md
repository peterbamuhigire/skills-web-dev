---
name: ux-principles-101
description: 101 actionable UX principles covering accessibility (WCAG), controls, forms, navigation, search, empty states, onboarding, error recovery, progress indicators, copywriting, user journeys, and ethical design. Cross-cutting skill — load alongside...
---

# UX Principles 101

> Cross-cutting skill. Load alongside any platform or domain skill to enforce UX quality.

## Plugins (Load Alongside)

| Skill | When to combine |
|---|---|
| `webapp-gui-design` | Web app UI implementation |
| `jetpack-compose-ui` | Android Compose screens |
| `form-ux-design` | Deep form patterns |
| `pos-sales-ui-design` | Point-of-sale interfaces |
| `healthcare-ui-design` | Clinical-grade UI |
| `ux-psychology` | Cognitive science foundations |
| `laws-of-ux` | Named-law quick reference (Fitts, Hick, Miller) |
| `interaction-design-patterns` | Tidwell's 45+ structural patterns |
| `web-usability-krug` | Krug's usability laws and billboard design |
| `lean-ux-validation` | Hypothesis-driven validation |
| `vibe-security-skill` | Security baseline (mandatory for web apps) |

---

## 1. Accessibility (WCAG Essentials)

Sources: Grant Ch.59-69, Maioli Ch.6 (POUR + Universal Design)

### Contrast & Colour

- **4.5:1 minimum** contrast ratio (WCAG 2.0 §1.4.3); aim for **7:1** on mobile
- **3:1 minimum** for large text (18px+) and non-text UI components
- Never use colour alone to convey information — 8% of men are colour-blind
- Colour is a great *secondary* indicator alongside text, icons, or patterns

### Keyboard & Focus

- Logical **tab order** via `tabindex`; test by tabbing through every form and menu
- **Skip-to-content** link at page top (CSS-hidden for sighted users)
- Never remove `:focus` outlines — restyle them if needed, but keep them visible
- Allow **ESC** to close modals, drawers, and overlays

### Zoom & Responsive

- Never disable device zoom (`maximum-scale=1.0, user-scalable=no` is forbidden)
- Support **200% zoom** without horizontal scroll or content loss
- Mobile-first responsive design is a given, not optional

### Labels & Icons

- Every icon **must** have a visible text label — icons alone cause frustration
- Use consistent icon style across the product; never mix disparate sets
- Don't embed text inside icons (breaks translation and screen readers)
- Don't use obsolete metaphors (floppy disk for "save", rotary phone)

### Touch Targets

- Finger-sized: max **5 tappable items** across screen width
- **2mm padding** between adjacent touch targets to prevent mis-taps
- Use native control elements (already the right size)

### Links & Copy

- Links must make sense **out of context** ("Download report" not "click here")
- Underline links or style them clearly — hover-only fails on touch screens
- Don't make non-links look like links or non-buttons look like buttons

### POUR Principles (Maioli)

- **Perceivable:** Content available to all senses (alt text, captions, contrast)
- **Operable:** Keyboard navigable, sufficient time, no seizure triggers
- **Understandable:** Readable, predictable, input assistance
- **Robust:** Works with current and future assistive technologies

### Universal Design — 7 Principles (Maioli)

1. Equitable use
2. Flexibility in use
3. Simple and intuitive
4. Perceptible information
5. Tolerance for error
6. Low physical effort
7. Size and space for approach and use

### Quick Accessibility Checklist (Maioli)

- Validate HTML for semantic correctness
- Test keyboard-only navigation end to end
- Use SVG over icon fonts (better screen-reader support)
- Maintain heading hierarchy (h1 > h2 > h3, no skipping)
- Avoid justified text (uneven word spacing harms dyslexic readers)
- Respect `prefers-reduced-motion` for all animations
- Don't auto-play audio or video

---

## 2. Controls & Buttons

Source: Grant Ch.6-15

- **Ellipsis (...)** in a button label means "further step required before action"
- Buttons must **look like buttons** — flat text is not a button; add affordances
- The **entire button area** is clickable, not just the label text
- Show pointer cursor on hover (desktop); give visual click feedback
- Don't invent arbitrary controls — use platform-standard components
- **Search** = text field + button labelled "Search"; magnifying glass icon only for search
- **Sliders** for subjective/qualitative values only (volume, brightness) — never for precise numbers
- **Numeric fields** (`<input type="number">`) for exact integer entry
- **Dropdowns** for >5 options; **radio buttons** for 2-5 options
- Group buttons by function; size per Fitts' Law (big enough to hit, spaced to avoid mis-clicks)
- Always allow **undo** for destructive actions (toast + undo control, grace period)

---

## 3. Forms & Input

Source: Grant Ch.34-54

### Password & Auth

- Default obfuscated; **show/hide toggle mandatory**
- Always allow **paste** into password fields (supports password managers)
- Don't require typing password twice — use the toggle instead
- Show strength rules while user types
- Pre-fill username in **"Forgot Password"** if already attempted sign-in
- **Case-insensitive** for usernames and emails; case-sensitive for passwords only

### Validation

- Validate **on blur** (per-field), not on submit
- Show **which field** needs attention (highlight + inline message)
- Never show only a generic "there was an error" banner
- Suggest corrections for common mistakes ("Did you mean gmail.com?")
- **Never clear** user-entered data on error or page reload

### Input Flexibility

- Accept spaces, dashes, brackets in phone numbers — parse server-side
- Allow hyphens, apostrophes, special characters in names
- Accept varied postal code formats; offer live lookup if possible
- Don't add decimal places to currency fields — let the user type them
- Match field width to expected content length
- Use device-native input: `type="tel"`, `type="email"`, system date pickers

### Email

- No client-side regex validation (too many false rejections with 1000+ TLDs)
- Use `<input type="email">` and verify server-side with a one-click link

### Payment Cards

- Bare minimum: card number, expiry, CVC — nothing else
- One field for full card number; silently strip spaces
- **HTTPS only** for card collection — no exceptions
- Always confirm the amount back to the user before charging

### Image Uploads

- Offer file picker **and** camera capture
- Allow multiple uploads in one action
- Provide crop and rotate; accept JPEG, PNG, GIF minimum
- Show upload progress

### General Form Rules

- Don't ask for more than you need — every extra field reduces conversion
- Explain why you collect data and how you use it
- Use the same date picker control consistently across the product
- Don't move the UI while the user is interacting (reserve space for async elements)

---

## 4. Navigation & Content

Source: Grant Ch.16-27, 83-84, 92-98

### Scroll & Pagination

- **Infinite scroll** for feed-style content only (news, photos)
- **Pagination** for finite/structured content (emails, orders, search results)
- Store user's **scroll position** on navigate-away; restore on return
- Show edges of off-screen items as visual cues that more content exists

### Menus & Discoverability

- Don't hide items in **hamburger menus** — kills discoverability and orientation
- If hamburger is unavoidable, label it "Menu"
- Prefer bottom nav, tabbed nav, or visible sidebar
- Group menu items into sections (Miller's Law: 7 plus-or-minus 2)
- Hide **advanced settings** behind progressive disclosure
- Repeat key nav items in the **footer**; don't make footer a dead end

### Links

- Links must **look like links** (underlined or clearly distinct)
- Don't make non-links look clickable

### Content Patterns

- "Show, don't tell" — on-screen tips beat long text descriptions
- Users don't read; they scan — use visual hierarchy
- Video demos great for complex features; must be skippable
- Build on **established metaphors** (Jakob's Law) — users want your product to work like others they know
- Pick good **defaults** — most users never change them
- Decide: is this interaction **obvious** (always visible), **easy** (findable), or **possible** (tucked away)?
- Follow standard **messaging** patterns: unread count, grouped inbox, thread view, "return" for new line not send

---

## 5. Search UX

Source: Grant Ch.11, 82, 91

- Search field = text input + button labelled "Search"
- Auto-focus search field when Search tab is tapped (mobile)
- **Categorise** results into sections (products, pages, help articles) with counts
- Most relevant result at **top** — don't promote paid results over organic
- Handle **zero results** gracefully: spelling suggestions, related queries, guidance
- Provide sort and filter controls for large result sets
- Test popular search terms to verify relevance
- For dropdowns with many options, add a **search/filter** inside the dropdown

---

## 6. Empty States & Onboarding

Source: Grant Ch.20-21, 74, 77-78, 80; Maioli SSI

### Blank Slates

- Empty views must show **helpful content + CTA** (not just "No items")
- Be task-oriented: tell users what to do next, be specific per feature
- Blank slates display once — ideal moment for orientation

### Three System States to Design For (Maioli — System State Inventory)

1. **New user (empty):** Guided content, sample data, getting-started tips
2. **Typical use:** The standard UI with real data
3. **Extreme/overloaded:** Graceful handling of large data sets, edge cases

### Onboarding Rules

- "Getting Started" tips must be **easily dismissable** in one action
- If your UI requires extensive explanation, simplify the UI instead
- Don't nag users to **rate the app** — include a quiet link for motivated users
- Don't use **vanity splash screens** — show a layout skeleton instead
- Users don't care about your company's mission statement — show value immediately

### Returning Users

- **"Create from Existing"** shortcut: duplicate + edit beats starting from scratch
- Respect prior context — pre-fill, remember preferences, restore state

---

## 7. Progress & Feedback

Source: Grant Ch.55-58

| Task type | Indicator | Rule |
|---|---|---|
| Determinate (known duration) | **Linear progress bar** | Single bar, clear start/end, never sequential sub-bars |
| Indeterminate (unknown duration) | **Spinner** | Animated to show activity; remove on error |
| Never | Looping animated progress bar | Filling to 100% then restarting is dishonest |

- Show **numeric progress** (percentage or "3 of 7") if there is time to read it
- For long processes, show estimated **time remaining** (or % if estimate unreliable)
- Provide feedback within **400ms** (Doherty Threshold from Laws of UX)
- Keep micro-animations short and subtle; respect `prefers-reduced-motion`

---

## 8. Error Recovery

Source: Grant Ch.15, 45-47; Maioli severity scale

### Validation Flow

1. Validate **on blur** (per-field) with inline messages
2. Summarise remaining errors **on submit**
3. Highlight the specific field + show constructive message
4. Never clear form data on validation failure

### Error Message Rules

- Clear, simple, constructive — never intimidating or blame-the-user
- Tell user **what went wrong** and **how to fix it**
- Use active voice ("Enter a valid email" not "Email is invalid")

### Destructive Actions

- **Undo** for reversible destructive actions (toast + undo control, grace period)
- **Confirmation dialog** for irreversible actions ("Delete account?")
- Always provide an escape hatch — user control and freedom

### Nielsen Severity Scale (Maioli)

| Rating | Severity | Action |
|---|---|---|
| 0 | Not a usability problem | No action |
| 1 | Cosmetic | Fix when convenient |
| 2 | Minor | Low priority fix |
| 3 | Major | High priority — fix before next release |
| 4 | Catastrophe | **Must fix before release** |

---

## 9. User Journeys

Source: Grant Ch.70-81

- Every journey has a **beginning, middle, and end** — signpost each stage
- User always knows their **current stage** (progress indicator, breadcrumbs, landmarks)
- **Breadcrumb navigation** for deep hierarchies — well-understood, rarely misused
- **"Skip This"** for optional steps — never trap users in non-essential flows
- Show **unsaved work indicator** (bullet, "not saved" text in title bar)
- Consider autosave where appropriate
- Follow **standard e-commerce** pattern: products (searchable, sortable, add-to-cart) > basket (modify, remove) > checkout (details, payment, guest option)
- Make it **easy to pay** — simple pricing page, obvious buy buttons, minimal form
- Test payment flows regularly
- Make your **favicon** distinctive and legible at 16px
- Don't build custom back buttons that replicate browser behaviour

---

## 10. Copywriting for UI

Source: Grant Ch.85-90

### Standard Terminology

| Use this | Not this |
|---|---|
| Sign in | Log in, logon |
| Sign out | Log out, logoff |
| Sign up | Register |
| Forgot password | Reset your password, Can't access your account |

### Writing Rules

- **Consistent terminology** — same action = same word everywhere ("cart" not "cart/basket/bag")
- Write **like a human** — "Edit customer details" not "Edit customer"
- **Active voice** over passive: "Restart your computer to apply updates" not "Your computer must be restarted"
- User-centric language, never developer-centric or corporate-speak
- Don't let brand voice override clarity
- Continually review copy; test phrases with real users

---

## 11. Ethical Design

Source: Grant Ch.99-101; Maioli dark patterns

### Dark Patterns to Explicitly Avoid

- Sneaked items in cart (insurance, warranties auto-added)
- Promoted/fake results disguised as organic search results
- Ads that look like content or navigation
- Silently changing privacy settings or pre-checking marketing opt-ins
- Confusing unsubscribe flows (multiple steps, guilt-tripping copy)
- Full-screen "rate this app" nag dialogs
- Addictive design patterns that exploit psychological vulnerabilities

### Testing Imperative

- Test with **5 real users** — finds **85%** of usability problems (NNG Poisson distribution)
- Test with diverse ages, genders, abilities, and technical experience
- Test early (even paper prototypes); test often
- Users won't tell you what is wrong — they will just leave
- Don't test with colleagues or your boss — they are not real users

### Brand vs UX

- Nobody cares about your brand — they care what your product lets them do
- The UX **is** the brand; fight for the user, not the brand guide
- Reject brand guidelines that break: contrast, readability, usability, or accessibility

---

## 12. Heuristic Evaluation Quick Reference

Source: Maioli Ch.2 — Nielsen's 10 Usability Heuristics

1. **Visibility of system status** — keep users informed with timely feedback
2. **Match between system and real world** — use familiar language and conventions
3. **User control and freedom** — undo, redo, emergency exits
4. **Consistency and standards** — same words, actions, situations mean the same thing
5. **Error prevention** — eliminate error-prone conditions; confirm before destructive actions
6. **Recognition rather than recall** — make options visible; minimise memory load
7. **Flexibility and efficiency of use** — accelerators for experts, simple paths for novices
8. **Aesthetic and minimalist design** — every extra unit of information competes with relevant info
9. **Help users recognise, diagnose, and recover from errors** — plain language, suggest solution
10. **Help and documentation** — easy to search, focused on user tasks, concise

### Conversion Statistics (Maioli)

- Average e-commerce conversion rate: **2-3%**
- Every friction point compounds abandonment
- Fixing the top severity-4 issues yields the largest conversion gains

---

## 13. UX Quality Checklist

### Accessibility

- [ ] Contrast ratios pass WCAG (4.5:1 body / 3:1 large text)
- [ ] All icons have visible text labels
- [ ] Keyboard navigation works end to end (tab order, skip link, ESC closes modals)
- [ ] Colour is never the sole information channel
- [ ] Device zoom is not disabled; 200% zoom works
- [ ] Heading hierarchy is correct (h1 > h2 > h3)
- [ ] Focus outlines are visible (not removed)

### Controls & Forms

- [ ] Buttons look like buttons; links look like links
- [ ] Touch targets are finger-sized with 2mm padding
- [ ] Password fields have show/hide toggle and allow paste
- [ ] Forms validate per-field on blur with inline messages
- [ ] User data is never cleared on error
- [ ] Input formats are forgiving (spaces, dashes, special characters)

### Navigation & Content

- [ ] Empty states have helpful content + CTA
- [ ] Infinite scroll used only for feeds; pagination for structured content
- [ ] Scroll position is preserved on navigate-away and return
- [ ] Hamburger menu avoided or labelled "Menu"

### Progress & Errors

- [ ] Progress indicators match task type (bar vs spinner)
- [ ] Feedback appears within 400ms
- [ ] Destructive actions have undo or confirmation dialog
- [ ] Error messages are specific, constructive, and non-intimidating

### Copy & Ethics

- [ ] "Sign in" / "Sign up" / "Forgot password" terminology used
- [ ] Consistent terminology throughout product
- [ ] Active voice in all UI copy
- [ ] No dark patterns (sneaked items, fake results, pre-checked opt-ins)
- [ ] Tested with 5+ real users

---

## Typography Quick Reference

Source: Grant Ch.1-5

- Max **two typefaces**: one for headings, one for body
- Prefer the **system font stack** for body copy (faster, renders better)
- Body copy: **16px**, **1.5 line height**, default character spacing
- Use **2-3 type sizes** to depict information hierarchy (headline > subtitle > body)
- Never disable device text scaling

---

*Sources: 101 UX Principles (Grant, 2018), Fixing Bad UX (Maioli, 2018)*
