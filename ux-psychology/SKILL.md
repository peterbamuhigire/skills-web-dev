---
name: ux-psychology
description: Foundational cognitive science for design. Covers dual-process thinking, memory limits, attention, Gestalt, motivation (SDT), cognitive biases, dark patterns, and design laws (Fitts, Hick-Hyman, Von Restorff). Referenced by all design skills. Load this skill whenever you need to make design decisions grounded in how humans actually think.
---

# UX Psychology — Cognitive Science Foundations

Grounded in Hodent (2022), Panzarella (2022), Paduraru (2024), and Klein (2013).

## When to Use

Load alongside any design skill when:
- Making layout, navigation, or interaction decisions
- Writing error messages, labels, or instructional copy
- Designing onboarding, motivation, or engagement systems
- Evaluating whether a design respects how users actually think

---

## 1. Dual-Process Model (System 1 / System 2)

**System 1** — Fast, automatic, effortless. Handles routine actions, conditioned responses, pattern recognition. Deeply biased but very efficient.

**System 2** — Slow, deliberate, resource-intensive. Handles complex reasoning. Does not naturally override System 1.

**Design rule:** Most users interact via System 1. They are not reading every element — they are scanning, pattern-matching, and satisficing. Design for low-effort, intuitive interaction. Reserve System 2 demands only for genuinely complex decisions.

**Satisficing:** Users stop reading at the point they believe they have enough information. Put critical content first — never at the end of labels or instructions.

---

## 2. Memory

Three components — all matter for design:

**Sensory memory** — holds input for under 1 second. If not attended to, it is lost.

**Working memory** — extremely limited capacity (~3–4 chunks), easily disrupted, requires attentional resources. This is where encoding happens. Every time a user switches context, they lose what was held here.

**Long-term memory:**
- *Explicit* — consciously retrievable facts/episodes; fallible; every retrieval is a reconstruction
- *Procedural/muscle memory* — deeply encoded habits and patterns; very durable; violated conventions force users back to System 2

**Miller's Law** — Working memory holds ~7 (±2) items; in practice, 3–5 is a safer design target.
- Group interface elements into ≤7 chunks per region; aim for ≤5
- Apply chunking: break phone numbers, IBANs, and codes into groups (555-867-5309, not 5558675309)

**Serial Position Effect** — Users best remember the first (primacy) and last (recency) items in a list. Middle items are least memorable.
- Place the most important navigation or menu items first or last — never in the middle
- Order destructive or rarely used actions last

**Zeigarnik Effect** — Incomplete tasks are remembered better than completed ones; open loops create cognitive pull.
- Progress bars, step indicators, and "Your profile is 60% complete" prompts leverage this — open loops draw users back

**Design rules:**
- Never rely on users remembering instructions from a previous screen
- Never rely on your own memory — document everything
- Respect established conventions (back button, Ctrl+S, swipe-to-delete) — breaking them is always costly
- Recognition beats recall: show options, recent items, and suggestions rather than requiring typed recall

---

## 3. Attention

**Attention is scarce, finite, and easily depleted.** It works as a filter: focusing on one thing means filtering everything else.

**Change blindness** — large changes can go completely unnoticed if the user's attention is elsewhere. Animate or highlight changes to ensure they are seen.

**Multitasking** — largely a myth for cognitive tasks. Tasks sharing attentional demand compete; users degrade in both.

**Three types of cognitive load:**
| Type | What it is | Strategy |
|------|-----------|----------|
| Intrinsic | Task's inherent complexity | Scaffold with wizards, step indicators, progressive disclosure |
| Extraneous | Complexity from poor design | Remove, simplify, group, hide |
| Germane | Effort to build mental models | Reinforce with consistent patterns, meaningful defaults |

**Selective Attention** — Users filter out information irrelevant to their current goal. Anything outside their task path is effectively invisible.
- Never rely on users noticing elements placed outside their active task flow
- Test where users actually look, not where you placed things

**Paradox of the Active User** — Users never read manuals; they start using the product immediately and muddle through without reading instructions.
- Embed onboarding in the product flow; documentation that requires reading first will be ignored
- Design for learning-by-doing, not reading-before-doing

**Design rules:**
- Reduce extraneous cognitive load ruthlessly
- New users face maximum intrinsic load — onboard progressively
- Visual hierarchy and contrast direct attention — use them deliberately

---

## 4. Perception & Gestalt

Perception is a subjective construction — not a faithful recording. Context, culture, and expectations all shape what users perceive.

**Key Gestalt principles:**
- **Proximity** — elements close together are perceived as grouped
- **Similarity** — elements sharing attributes (colour, shape, size) are grouped
- **Common Region** — elements inside a shared boundary (card, panel, divider) are grouped, even without other visual similarity
- **Uniform Connectedness** — elements connected by a visible line are perceived as more strongly related than proximity alone
- **Prägnanz (Law of Good Form)** — users perceive the simplest, most stable interpretation of any ambiguous visual; favour clean, unambiguous shapes
- **Figure-Ground** — primary content must stand out from background; use whitespace deliberately
- **Continuity** — aligned elements guide the eye along a path
- **Closure** — users complete incomplete shapes mentally

**Mental Model** — Users approach your product with expectations built from prior experience with other apps, physical analogies, and conventions.
- Align with users' existing mental models; violation requires explicit explanation
- Jakob's Law: users spend most of their time on other products — they expect yours to work the same way

**F-Pattern and Z-Pattern:**
- F-Pattern: text-heavy pages; users read top, then scan down the left side
- Z-Pattern: sparse pages; top-left → top-right → diagonal down → bottom-right
- Place key information and CTAs along these natural scan paths

**Design rules:**
- Never rely on colour alone to communicate meaning (4–10% of users have colour vision deficiency)
- Icons and metaphors are culture-dependent — test across demographics
- Use contrast (size, weight, colour, space) to establish clear reading order

---

## 5. Motivation (Self-Determination Theory)

**SDT — the most robust framework for intrinsic motivation.** Three needs must be satisfied:

1. **Competence** — a growing sense of skill and control; feeling increasingly capable
2. **Autonomy** — meaningful choices; self-expression; not forced into rigid paths
3. **Relatedness** — social connection; actions that connect to others or shared purpose

**Why this matters:** Products that satisfy these three needs generate intrinsic engagement. Products that only offer extrinsic rewards (badges, points, streaks) produce fragile engagement that collapses when rewards stop.

**Emotion and cognition** are inseparable. Emotional design operates at three levels (Norman):
1. **Visceral** — immediate, automatic response to appearance
2. **Behavioral** — functional performance; does it work well?
3. **Reflective** — intellectual response; what values does using this product project?

All three levels are always active. Neglect any one of them and the experience is incomplete.

**Design rule:** Gamification (badges, points) only addresses extrinsic motivation. For genuine engagement, target competence, autonomy, and relatedness.

**Flow (Csikszentmihalyi)** — Deep engagement emerges when challenge exactly matches skill level. Too easy = boredom; too hard = anxiety.
- Match task difficulty to the user's current skill level; scaffold progressively as competence grows
- Immediate, unambiguous feedback is a prerequisite for flow — latency or ambiguity breaks the state

**Peak-End Rule (Kahneman)** — Users judge an experience primarily by its most intense moment (peak) and its ending — not duration or average quality.
- Design exceptional moments at key milestones (first success, first real value delivered)
- Ensure ending states (confirmation screens, completion flows) are delightful — not perfunctory
- Mitigate pain peaks (errors, long loading, failed submissions) as a priority over general polish

---

## 6. Cognitive Biases Every Designer Must Know

| Bias | What it is | Design implication |
|------|-----------|-------------------|
| **Curse of knowledge** | You cannot unsee what you know; obvious to you, invisible to users | Always test with people who have never seen your product |
| **Egocentric bias** | You assume others experience the world as you do | You are never your user — research is non-optional |
| **IKEA effect** | You overvalue things you helped build | You are a poor judge of your own product's quality |
| **Hindsight bias** | Everything seems obvious after you know the outcome | Bad decisions looked fine at the time — document your reasoning |
| **Confirmation bias** | You seek data that confirms what you already believe | Actively look for disconfirming evidence in research |
| **Status quo bias** | Users prefer inaction and existing defaults | Design defaults thoughtfully — they determine most outcomes |
| **Loss aversion** | Losing hurts more than equivalent gaining pleases | Sunk-cost thinking is predictable; don't exploit it at users' expense |
| **Goal-gradient effect** | Motivation increases as users approach a goal | Show progress indicators; make users feel they are nearly done |
| **Scarcity effect** | Items perceived as scarce are valued more; abundance *decreases* perceived value | "Only 3 left", limited availability, early-access — scarcity signals desirability |
| **Framing effect** | Context and presentation change perceived value independently of objective quality | Premium pricing, professional context, and quality signals literally change the experienced pleasure |
| **Anchoring effect** | The first piece of information seen sets a reference point; all subsequent judgements are relative to it | Show full price before discount; sequence options from expensive to cheap; first number anchors the comparison |
| **Endowed Progress Effect** | People are more motivated to complete a goal if they feel they have already made progress toward it | Give new users a head-start on profiles, progress bars, or completion meters — 82% higher completion vs. starting at 0 |
| **Social Proof & Authority** | People look to the behavior of others (especially similar others and authority figures) to guide their own decisions, particularly under uncertainty | User counts, expert endorsements, testimonials, and peer behavior signals reduce decision anxiety. Research base: Bandura's Social Learning Theory — people adopt behaviors they observe in relevant role models. Most effective when targeting users similar to the viewer, not just celebrities. |

---

## 7. Dark Patterns & Ethical Design

**Dark patterns** (Brignull): design that intentionally deceives users to extract value at their expense.

Common dark patterns:
- Pre-checked subscriptions
- Confirm-shaming ("No thanks, I don't want to save money")
- Hidden costs revealed at payment
- Obscured cancellation flows
- Making the desired action harder to find than the profitable one

**Grey-area patterns** — not technically deceptive but exploit biases for business gain at user expense:
- Loss aversion exploitation (expiring streaks, "you'll lose your progress")
- Fabricated scarcity ("only 1 left!")
- Opt-out defaults for data sharing, subscriptions, auto-renewal
- Auto-play without explicit consent
- Push notifications without genuine value

**How to distinguish nudge from dark pattern:**
A nudge changes behaviour for the long-term benefit of the user or society (seat belt reminder, exercise prompt). A dark pattern changes behaviour for business benefit at the user's expense. The test is: *whose interests are served?*

---

## 8. Design Laws

### Fitts's Law
Time to point at a target increases as target size decreases and distance increases.
- Make primary action buttons large and close to common starting positions
- Make destructive/accidental-click-risk buttons smaller and further away
- Minimum touch target: 44×44px (web), 48dp (Android)

### Hick-Hyman Law
Decision time increases logarithmically with the number of options.
- Present ≤7 options per group (aim for ≤5)
- Use categories and filtering to reduce apparent choice count
- Provide smart defaults to eliminate unnecessary decisions
- Indecision ("analysis paralysis") causes users to disengage entirely

### Von Restorff Effect
The more an element stands out, the better it is noticed and remembered.
- Use contrast, size, colour, and motion deliberately
- When too many elements compete for attention, nothing stands out

### Pareto Principle (80/20)
80% of user activity involves only 20% of features.
- Identify the core 20% and make them prominent
- Don't clutter the interface with rarely used features

### Jakob's Law
Users spend most of their time on other products. They expect yours to work the same way.
- Follow established conventions for navigation, search, forms, and interactions
- Innovation has a learning cost — deviate from convention only when the benefit clearly outweighs it

### Aesthetic-Usability Effect
Aesthetically pleasing designs are perceived as easier to use, even when they aren't.
- Polish UI — users tolerate minor usability problems in beautiful interfaces
- This effect fades with repeated exposure; function must ultimately deliver

### Doherty Threshold
When system response time drops below 400ms, users stay engaged; above 400ms attention breaks.
- Target <100ms for perceived-instant feedback; <400ms for any interactive action
- Use skeleton screens, optimistic UI, and progress indicators when performance cannot be guaranteed

### Tesler's Law (Law of Conservation of Complexity)
Every system has inherent complexity that cannot be eliminated — only moved.
- Simplifying the UI shifts complexity to the backend or documentation
- Decide consciously who bears the complexity: the product or the user

### Occam's Razor
Among competing designs, prefer the simplest one that adequately solves the problem.
- Remove every element that does not serve a clear purpose; when in doubt, leave it out

### Parkinson's Law
Work expands to fill the time available — and users fill whatever input space they are given.
- Set time constraints on tasks to create urgency; don't provide more input space than needed

### Postel's Law (Robustness Principle)
Be conservative in what you send; be liberal in what you accept.
- Accept varied input formats (phone with/without dashes, dates in multiple formats)
- Validate with helpful correction, not rejection: "We'll format that" not "Invalid input"
- Return consistent, clean, predictable output regardless of input variation

### Choice Overload
Too many options reduces satisfaction and increases the likelihood of no decision at all.
- Cap primary choices at ≤5; use categories and filtering for large option sets
- Provide a recommended default — most users will take it; it eliminates unnecessary decisions

---

## 9. Key Mantras

1. **"You are not your users."** — the cardinal rule of UX
2. **"We don't design an experience; we design for an experience."** — Hodent. Experiences happen in the user's mind.
3. **"Design for System 1."** — Most interactions happen automatically; remove the need for deliberate effort
4. **"Recognition over recall."** — Show options; don't make users remember
5. **"Satisficing is always happening."** — Users stop reading when they think they have enough. Put critical content first.
6. **"People don't want a drill; they want to install bookshelves."** — Norman. Design for outcomes, not features.
7. **"Convention violation is always costly."** — Breaking established patterns forces users into System 2.
8. **"Defaults are decisions."** — Most users never change defaults; design them thoughtfully.

---

## 10. Tidwell's Behavioral Design Patterns (Cross-Reference)

The `interaction-design-patterns` skill provides Tidwell's 12 behavioral patterns that complement the cognitive science above. Each Tidwell pattern has a direct cognitive foundation:

| Tidwell Pattern | Cognitive Foundation |
|----------------|---------------------|
| **Satisficing** | System 1 + working memory limits — users satisfice because parsing is work |
| **Habituation** | Procedural memory — habituated gestures bypass conscious thought |
| **Spatial Memory** | Procedural + explicit memory — location is encoded as part of the learned pattern |
| **Deferred Choices** | Cognitive load — unnecessary decisions increase extraneous load |
| **Instant Gratification** | Motivation (SDT) — early competence feelings drive continued engagement |
| **Safe Exploration** | Anxiety reduction (Emotion Mind) — fear of mistakes suppresses exploration |
| **Incremental Construction** | Flow state (Csikszentmihalyi) — immediate feedback is prerequisite for flow |
| **Streamlined Repetition** | Habituation + efficiency — reduce System 2 demand on routine tasks |
| **Prospective Memory** | Prospective memory theory — externalising reminders offloads working memory |
| **Social Proof** | Loss aversion + relatedness (SDT) — peer behaviour reduces decision uncertainty |

**Load `interaction-design-patterns` alongside this skill for the full pattern library.**

**Load `habit-forming-products` when designing for repeat, unprompted engagement.** That skill operationalises the IKEA effect, goal-gradient, scarcity, framing, anchoring, and endowed progress into the Hook Model (Trigger → Action → Variable Reward → Investment).

**Load `laws-of-ux` when you need to cite or look up any named UX law by name.** That skill is the complete named-law quick-reference for all 30 Yablonski Laws of UX with design rules, grouped by law family.

---

## Sources

- Hodent, C. (2022). *What UX Is Really About.* CRC Press.
- Panzarella, L. (2022). *UI/UX Web Design Simply Explained.*
- Paduraru, E. (2024). *Roots of UI/UX Design.* Creative Tim.
- Norman, D. (2013). *The Design of Everyday Things.* Basic Books.
- Kahneman, D. (2011). *Thinking, Fast and Slow.* Farrar, Straus and Giroux.
- Tidwell, J., Brewer, C., Valencia, A. (2020). *Designing Interfaces*, 3rd ed. O'Reilly.
- Eyal, N. & Hoover, R. (2014). *Hooked: How to Build Habit-Forming Products.* Portfolio/Penguin. (Scarcity, Framing, Anchoring, Endowed Progress, Social Proof effects)
- Bandura, A. (1977). *Social Learning Theory.* Prentice Hall. (Social Proof / observational learning)
- Yablonski, J. (2024). *Laws of UX*, 2nd ed. O'Reilly. (lawsofux.com — all named laws)
- Csikszentmihalyi, M. (1990). *Flow: The Psychology of Optimal Experience.* Harper & Row.
- Miller, G. A. (1956). "The Magical Number Seven, Plus or Minus Two." *Psychological Review.*
