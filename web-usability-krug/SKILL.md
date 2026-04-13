---
name: web-usability-krug
description: Steve Krug's web and mobile usability principles from Don't Make Me Think
  (3rd ed.). Load when designing web or mobile interfaces, navigation, home pages,
  forms, or planning usability testing. Covers Krug's 3 Laws, scanning behaviour,
  Billboard...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Web Usability — Krug's Principles

<!-- dual-compat-start -->
## Use When

- Steve Krug's web and mobile usability principles from Don't Make Me Think (3rd ed.). Load when designing web or mobile interfaces, navigation, home pages, forms, or planning usability testing. Covers Krug's 3 Laws, scanning behaviour, Billboard...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `web-usability-krug` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Grounded in Krug, S. (2014). *Don't Make Me Think, Revisited*, 3rd ed. New Riders.

## When to Use

Load alongside `ux-psychology` when:
- Designing web or mobile UI layouts, navigation, or page structure
- Writing labels, headings, or instructional copy
- Planning a home page or onboarding flow
- Conducting or planning usability tests
- Evaluating whether a design treats users with courtesy

---

## 1. Krug's Three Laws of Usability

**First Law: Don't make me think.**
Every page should be self-evident — users should understand what it is and how to use it without deliberate effort. Eliminate every "question mark" that appears above users' heads: ambiguous links, clever-but-unclear labels, visual elements whose purpose is unclear.

**Second Law: Clicks don't matter, cognitive effort does.**
Users will happily click many times if each click is mindless and confident. Depth is never the enemy — ambiguity is. A three-click path with clear choices beats a one-click path that makes the user stop and think.

**Third Law: Omit needless words.**
Cut the word count in half. Then cut half of what remains. Happy talk, preambles, and instructions users won't read add noise and hide the signal.

---

## 2. How Users Really Use the Web

**We don't read — we scan.**
Users glance at a page, seize the first reasonable match to their goal, and click. They rarely read anything in full. Design for scanning, not reading.

**We don't optimise — we satisfice.**
Users don't find the best option; they take the first option that seems good enough. The first plausible link wins. Design the most important path to be unmissably obvious.

**We don't figure things out — we muddle through.**
Most users never read instructions or build accurate mental models. They click until they find it. This is not stupidity — it is rational under time pressure. Design to support muddling without penalty, not to require comprehension first.

---

## 3. Billboard Design 101 — Six Scanning Principles

Apply these to every page, in order of impact:

1. **Take advantage of conventions.** Use established patterns (logo top-left, search top-right, blue underlined links). Innovation has a learning cost — deviate only when the benefit is unmistakable.

2. **Create effective visual hierarchies.** The visual weight of every element should reflect its importance. Important = prominent. Related = visually grouped. Parent-child relationships = nested or indented.

3. **Break pages into clearly defined areas.** Users need to quickly decide which areas are relevant. Defined regions (cards, panels, whitespace) let users skip entire sections at a glance.

4. **Make clickables obvious.** Buttons must look clickable. Links must look like links. Underlines and colour distinguish links from body text. When in doubt, add a visual affordance.

5. **Eliminate distractions.** Three types of noise: unnecessary animation, too many promotions, and clutter. Every non-essential element competes with essential ones. Remove what isn't earning its place.

6. **Format text to support scanning.** Use headings that stand alone as labels. Use bullets for lists. Highlight key terms. Short paragraphs. White space is content — it separates signal from noise.

---

## 4. Navigation Design

Navigation does three things beyond wayfinding: it tells users what's here, it tells them how to use the site, and it builds confidence in the people behind it.

### Persistent Navigation Elements (every page except checkout)

| Element | Rule |
|---------|------|
| **Site ID / Logo** | Top left; always links to home |
| **Sections** | Primary navigation; reflect top-level information architecture |
| **Utilities** | Secondary nav (Sign in, Help, Cart); less prominent than sections |
| **Search** | Simple text box with a button labelled "Search"; top right |

### Page-Level Navigation Rules

- **Page name:** Must match what was clicked to get there — exactly. This confirms the user arrived correctly.
- **"You are here" indicator:** Highlight the current location in navigation. Users land deep via search; they need context.
- **Breadcrumbs:** Show full path from home. Use `>` separator. Bold the final item (current page). Don't replace page name.
- **Local navigation:** Show sub-sections of the current section; don't bury sub-sections in a dropdown that closes.

### The Trunk Test

Drop any user on any page, hold it at arm's length, and ask them to identify — without clicking — the answers to these six questions:

1. What site is this? (Site ID)
2. What page am I on? (Page name)
3. What are the major sections? (Sections)
4. What are my options at this level? (Local navigation)
5. Where am I in the scheme of things? ("You are here" indicator)
6. How can I search? (Search)

If users cannot answer all six in seconds, navigation needs work.

---

## 5. Home Page Design — The Big Bang Theory

First impressions are formed in seconds and are almost irreversible. The home page must instantly answer four questions:

1. **What site is this?** — Name and tagline make this clear immediately.
2. **What can I do here?** — Primary actions are obvious, not buried.
3. **Where do I start?** — One clear entry point leads the eye.
4. **Why should I be here and not somewhere else?** — Tagline conveys unique value.

**Tagline ≠ motto.** A tagline conveys specific benefit and differentiation ("The World's Largest Selection of Widgets"). A motto expresses a principle ("Delivering Excellence"). Mottoes are useless on a home page that users don't already know.

**The home page must do more with less.** It must serve first-time visitors, returning users, and every type of task — all at once. Ruthlessly prioritise. The top three user tasks must be dead obvious.

---

## 6. Usability as Common Courtesy — The Goodwill Reservoir

Every visit begins with a reservoir of user goodwill. Each friction event drains it. Each act of consideration refills it.

### Things That Drain Goodwill

| Anti-pattern | Why it erodes trust |
|---|---|
| **Hiding information users want** | Phone numbers, shipping costs, prices — forcing users to dig signals you value your interests over theirs |
| **Punishing wrong formatting** | Requiring no spaces in credit card numbers when spaces aid accuracy; rejecting phone formats you can easily normalise |
| **Asking for unnecessary data** | Every extra field is a demand for trust you haven't earned |
| **Faux sincerity** | "Your call is important to us" — disingenuous language is immediately recognised and resented |
| **Marketing in the way** | Hero images, promotional banners, and feel-good copy that delay access to content |
| **Amateurish appearance** | Sloppy, disorganised, inconsistent design undermines confidence in the organisation |

### Things That Refill Goodwill

- Make the top three tasks unmissably obvious and frictionless
- Be upfront about information users expect you to hide (shipping costs, limitations, outages)
- Save users steps wherever you can (pre-filled links, remembered preferences, single-click access)
- Show genuine effort in the quality and accuracy of your content
- Anticipate questions and provide honest, candid FAQs — not marketing FAQs (QWWPWAs)
- Recover gracefully from errors with clear, actionable messages
- Apologise explicitly when you can't do what users want

---

## 7. DIY Usability Testing

**Testing with 3 users once a month beats elaborate testing once a year.**

| Principle | Why it matters |
|---|---|
| **3 users per session is enough** | You hear the same critical problems after 3 sessions; more users adds cost but not insight |
| **One morning per month** | Regular cadence ensures testing informs decisions, not just reports |
| **Qualitative, not quantitative** | You're finding problems, not measuring satisfaction scores |
| **Focus groups ≠ usability tests** | Focus groups surface opinions; tests surface behaviour. They are not interchangeable. |
| **Watch, don't help** | Stay quiet. Helping is the observer's reflex — resist it. What the user struggles with is the data. |
| **Debrief the same day** | While it's fresh — list every problem; group by severity; pick top 3 to fix |
| **Fix the top problems first** | Don't try to fix everything. One well-fixed severe problem beats ten minor tweaks. |

**Get stakeholders in the room.** Watching users struggle live is more persuasive than any report. One stakeholder who watches a test becomes an internal advocate. A presentation about test results rarely is.

---

## 8. Mobile Usability

**The fundamental challenge:** Mobile has a fraction of the screen real estate of desktop. Tradeoffs are unavoidable. The question is which tradeoffs are acceptable — and the answer must never be: trading away usability.

### Key Mobile Principles

| Principle | Application |
|---|---|
| **Managing real estate ≠ removing usability** | Hiding navigation behind hamburgers reduces clutter but increases cognitive load. Test whether users can find what they need. |
| **Affordances must be visible** | Hover does not exist on touch screens. Buttons must look tappable without hover states. Visual cues that only appear on hover are invisible on mobile. |
| **Flat design removes useful signals** | Shadows, gradients, and borders that indicate clickability were removed in flat design trends. Flat interfaces require extra care to make affordances legible. |
| **Speed is a feature** | Mobile users are often on slower connections and more distracted. Every millisecond counts. Optimise aggressively. |
| **Learnability AND memorability** | An app users can learn quickly but forget by next week will be abandoned. Apps must be learnable on first use AND memorable on return. |
| **Mobile-first** | Design the constrained mobile experience first, then enhance for larger screens. Mobile-first forces ruthless prioritisation. |

### Mobile Usability Testing

Same process as desktop testing — tasks, think-aloud, silence from the observer. Logistics differ:
- Use a camera attached to the device (not just mirroring — you need to see gestures)
- Allow natural device-holding; tethered camera rigs let users move freely
- Screen mirroring without gesture capture makes tests nearly uninterpretable

---

## 9. Accessibility Essentials

Accessibility is not optional. It is profoundly the right thing to do — blind users with a screen reader can now read any newspaper or magazine independently. That level of impact is rare.

### Four Things to Do Now

1. **Fix usability problems that confuse everyone.** Confused sighted users → dramatically more confused screen-reader users. Usability and accessibility are not separate concerns.

2. **Add alt text to every image.** Descriptive alt text for meaningful images; null (`alt=""`) for decorative images. Screen readers read every image without alt text as its filename.

3. **Use heading elements correctly.** `<h1>` → page title; `<h2>` → major sections; `<h3>` → subheadings. Don't use headings for visual size — use CSS. Screen-reader users navigate by headings; bad heading structure = no structure.

4. **Form accessibility:**
   - Use `<label>` elements associated with every form field
   - Add a "Skip to Main Content" link at the top of every page
   - Ensure all interactive elements are keyboard-accessible (no mouse-only interactions)
   - High contrast between text and background — no light grey on dark grey

### Screen-Reader Insight

Screen-reader users scan with their ears. They listen to the first few words of a link or line, then skip. Keywords must be at the beginning of links and headings — not at the end. "Click here" links are useless. "Download the 2024 Annual Report" is not.

---

## 10. Definitive Rules (Always / Never)

| Rule | Applies to |
|---|---|
| **Never use small, low-contrast type** | Body text, labels, captions — contrast is not a style choice |
| **Don't put labels inside form fields** | Ghost text disappears on focus; users forget what the field is for; accessibility fails |
| **Preserve visited vs unvisited link colours** | Colour distinction shows where users have been; removing it is removing information |
| **Float headings toward the text they precede** | A heading separated from its body by equal whitespace above and below reads as a floating label, not a section head |
| **Never make users format input data** | Accept phone numbers with or without dashes; credit cards with or without spaces; normalise in code, not in error messages |

---

## 11. Key Mantras (Krug)

1. **"Don't make me think."** — The cardinal rule; self-evidence is always the goal.
2. **"Clicks don't matter; cognitive effort does."** — Depth is fine; ambiguity is not.
3. **"Get rid of half the words, then get rid of half of what's left."** — All copy on any page.
4. **"It's not rocket surgery."** — Usability testing does not require specialists or budgets. Just do it.
5. **"Whoever wins the usability debate wins nothing."** — Arguments about what users prefer are resolved by watching users. Test instead of debate.
6. **"You are not your user."** — Your intuitions about your product are the most dangerous data you have.
7. **"A site is not usable unless it's accessible."** — Accessibility is part of usability, not separate from it.

---

## Cross-Skill Architecture

| Skill | What it adds |
|---|---|
| `ux-psychology` | Cognitive science WHY — dual-process, memory, attention, biases that underlie Krug's observations |
| `laws-of-ux` | Named law quick-reference — Fitts, Hick, Miller, Jakob, Tesler, and 25 more |
| `lean-ux-validation` | Hypothesis-driven validation process — how to run structured experiments before building |
| `interaction-design-patterns` | Tidwell's 45+ patterns — concrete UI decisions for navigation, layout, actions, data display |
| `form-ux-design` | Form-specific UX — field grouping, validation, error messages, multi-step forms |

---

## Source

Krug, S. (2014). *Don't Make Me Think, Revisited: A Common Sense Approach to Web Usability*, 3rd ed. New Riders/Peachpit.
