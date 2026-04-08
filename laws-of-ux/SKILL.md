---
name: laws-of-ux
description: Comprehensive named-law quick reference for all 30 Laws of UX (Yablonski) plus classic design heuristics. Load when citing, applying, or evaluating any named UX law by name. Covers Fitts, Hick, Miller, Jakob, Tesler, Postel, Doherty, Zeigarnik...
---

# Laws of UX — Complete Reference

Sourced from Yablonski (2024) *Laws of UX*, O'Reilly; Csikszentmihalyi (1990); Kahneman (2011); Eyal (2014).

## When to Use

Load this skill when:
- Citing or explaining a named UX law by name
- Evaluating a design decision against established principles
- Writing design rationale or documentation
- Teaching UX principles to a team

**For deeper cognitive-science foundations:** Load `ux-psychology` alongside this skill.
**For applied engagement design:** Load `habit-forming-products`.
**For interaction patterns:** Load `interaction-design-patterns`.

---

## Quick Reference Table — All 30 Laws

| Law | Core Principle | Key Design Rule |
|-----|---------------|-----------------|
| **Aesthetic-Usability Effect** | Beautiful designs are perceived as easier to use, even when they aren't | Polish UI — users tolerate imperfections in attractive interfaces; but this fades with use |
| **Choice Overload** | Too many options leads to fewer decisions and lower satisfaction | Cap primary choices at ≤5; use filtering to manage large sets; always offer a recommended default |
| **Chunking** | Information grouped into meaningful units is easier to process and remember | Group related elements visually; break codes, numbers, and fields into chunks |
| **Cognitive Bias** | Systematic errors in thinking affect all users, always | Design to work with biases (defaults, anchoring, social proof), not against them |
| **Cognitive Load** | Mental effort has a finite budget; exceeding it causes errors and abandonment | Eliminate extraneous load; scaffold intrinsic load; build germane load via consistency |
| **Doherty Threshold** | System response <400ms keeps users engaged; ≥400ms breaks focus | Target <100ms for instant feel; use skeleton screens and optimistic UI above that |
| **Fitts's Law** | Time to click/tap a target rises as size decreases and distance increases | Primary actions: large + close. Destructive actions: small + distant. Min touch target: 44×44px |
| **Flow** | Deep engagement emerges when challenge exactly matches skill; too easy = boredom, too hard = anxiety | Match task difficulty to user skill; give immediate, unambiguous feedback; scaffold progressively |
| **Goal-Gradient Effect** | Motivation increases as users approach a goal | Show progress; make users feel nearly done; use endowed progress (pre-loaded steps) |
| **Hick's Law (Hick-Hyman)** | Decision time rises logarithmically with number of options | Present ≤7 options per group; provide smart defaults; filter rather than list |
| **Jakob's Law** | Users expect your product to work like products they already know | Follow conventions for navigation, search, forms; innovate only when benefit outweighs learning cost |
| **Law of Common Region** | Elements inside a shared boundary are perceived as grouped | Use cards, panels, and dividers to group related items — even without other visual similarity |
| **Law of Proximity** | Elements placed near each other are perceived as related | Space grouped items tightly; leave clear gaps between unrelated groups |
| **Law of Prägnanz** | Users perceive the simplest, most stable interpretation of ambiguous visuals | Use clean, unambiguous shapes; avoid visual clutter that creates false groupings |
| **Law of Similarity** | Elements sharing visual attributes (colour, shape, size) are perceived as grouped | Use consistent colour and shape to signal relationships; break similarity deliberately to signal difference |
| **Law of Uniform Connectedness** | Elements connected by a visible line are perceived as more strongly related than proximity alone | Use lines, arrows, and borders deliberately to show explicit relationships |
| **Mental Model** | Users approach your product with expectations built from prior experience | Align with users' existing mental models; violation requires explicit explanation |
| **Miller's Law** | Working memory holds ~7 (±2) items; 3–5 is a safer target | Group UI into ≤7 chunks per region; break codes and numbers into sub-groups |
| **Occam's Razor** | Among competing designs, prefer the simplest that adequately solves the problem | Remove every element that does not serve a clear purpose; when in doubt, leave it out |
| **Paradox of the Active User** | Users never read manuals; they start using the product immediately and muddle through | Embed onboarding in the product flow; design for learning-by-doing |
| **Pareto Principle (80/20)** | 80% of usage involves only 20% of features | Make the core 20% prominent; don't clutter with rarely used features |
| **Parkinson's Law** | Work (and input) expands to fill the space/time available | Set time constraints to create urgency; don't give users more input space than needed |
| **Peak-End Rule** | Users judge an experience by its most intense moment and its ending — not average quality | Design exceptional milestone moments; ensure endings (confirmation screens) are delightful; minimise pain peaks |
| **Postel's Law (Robustness Principle)** | Be conservative in output; be liberal in input | Accept varied input formats; validate with helpful correction, not rejection; return clean predictable output |
| **Selective Attention** | Users filter out anything outside their current goal path — it is effectively invisible | Don't rely on users noticing elements placed outside their task flow; test where users actually look |
| **Serial Position Effect** | Users best remember the first (primacy) and last (recency) items in a list; middle items are least memorable | Place most important navigation items first or last; never bury critical options in the middle |
| **Tesler's Law** | Every system has inherent complexity that cannot be eliminated — only moved | Simplifying UI moves complexity to backend or docs; decide consciously who bears it |
| **Von Restorff Effect** | The item that stands out most is best noticed and remembered | Use contrast, size, colour, and motion deliberately; when everything stands out, nothing does |
| **Working Memory** | A temporary, limited-capacity workspace that holds ~3–4 active chunks | Never require users to remember information across screens; surface it; recognition over recall |
| **Zeigarnik Effect** | Incomplete tasks are remembered better than completed ones; open loops create cognitive pull | Progress bars, partial completion states, and "X% complete" prompts leverage this to re-engage users |

---

## Gestalt Laws — Grouped Reference

The five core Gestalt principles apply at every level of layout:

| Principle | Rule |
|-----------|------|
| **Proximity** | Close = grouped |
| **Similarity** | Matching attributes = grouped |
| **Common Region** | Shared boundary = grouped (strongest) |
| **Uniform Connectedness** | Connected by line = explicitly related |
| **Prägnanz** | Simplest stable interpretation wins |
| **Figure-Ground** | Primary content must contrast with background |
| **Closure** | Users mentally complete incomplete shapes |
| **Continuity** | Aligned elements guide the eye |

---

## Performance Laws — Grouped Reference

These laws govern speed and complexity trade-offs:

| Law | Threshold | Rule |
|-----|-----------|------|
| **Doherty Threshold** | 400ms | Below = engaged; above = disengaged |
| **Fitts's Law** | 44×44px minimum | Target size × distance determines click time |
| **Hick's Law** | ≤7 options | Log growth: double options ≠ double time — but it adds up |
| **Miller's Law** | 7±2 chunks | Practical target: 3–5 per region |

---

## System Design Laws — Grouped Reference

These govern how complexity is distributed across a system:

| Law | What it conserves | Design implication |
|-----|-------------------|-------------------|
| **Tesler's Law** | Complexity | Simplifying UI moves complexity elsewhere |
| **Postel's Law** | Data quality | Be strict in output; forgiving in input |
| **Occam's Razor** | Cognitive cost | Remove anything that doesn't serve a purpose |
| **Parkinson's Law** | Effort | Space and time fill themselves — constrain them |

---

## Cross-Skill Architecture

| Skill | What it provides |
|-------|----------------|
| `ux-psychology` | Cognitive science foundations — WHY these laws work (dual-process, memory, attention, Gestalt, biases) |
| `laws-of-ux` | Named-law reference — WHAT each law states and its design rule (this skill) |
| `habit-forming-products` | Applied engagement — HOW to operationalise laws into repeat behaviour (Hook Model) |
| `interaction-design-patterns` | Tidwell's 45+ patterns — HOW to apply these principles to concrete UI decisions |

---

## Sources

- Yablonski, J. (2024). *Laws of UX*, 2nd ed. O'Reilly. (lawsofux.com)
- Csikszentmihalyi, M. (1990). *Flow: The Psychology of Optimal Experience.* Harper & Row.
- Kahneman, D. (2011). *Thinking, Fast and Slow.* Farrar, Straus and Giroux.
- Miller, G. A. (1956). "The Magical Number Seven, Plus or Minus Two." *Psychological Review.*
- Tesler, L. (1980). *The Law of Conservation of Complexity.* Xerox PARC.
- Postel, J. (1981). *RFC 793 — Transmission Control Protocol.* IETF.
- Fitts, P. (1954). "The Information Capacity of the Human Motor System." *Journal of Experimental Psychology.*
- Eyal, N. & Hoover, R. (2014). *Hooked.* Portfolio/Penguin.
