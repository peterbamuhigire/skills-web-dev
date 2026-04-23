---
name: data-visualization
description: Data visualization patterns from Storytelling with Data (Knaflic, 2015)
  — the 6-lesson framework for transforming raw data into compelling visual stories
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Data Visualization — Storytelling with Data
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Data visualization patterns from Storytelling with Data (Knaflic, 2015) — the 6-lesson framework for transforming raw data into compelling visual stories
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `data-visualization` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | Data visualisation review | Markdown doc applying Knaflic's six-lesson framework to the dashboard or report under review | `docs/ux/dataviz-review-checkout.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
> Source: *Storytelling with Data* by Cole Nussbaumer Knaflic (Wiley, 2015)

## The 6-Lesson Framework

1. **Understand the context** — Who, What, How before any visual
2. **Choose an appropriate visual** — Match chart type to data + message
3. **Eliminate clutter** — Remove everything that does not add informative value
4. **Focus attention** — Use preattentive attributes to direct the eye
5. **Think like a designer** — Affordances, accessibility, aesthetics, acceptance
6. **Tell a story** — Beginning (plot), middle (twists), end (call to action)

---

## Lesson 1: Context First

### The Exploratory vs Explanatory Distinction

- **Exploratory** = hunting for pearls in oysters (100 hypotheses, maybe 2 findings)
- **Explanatory** = presenting the pearls (the specific story you want to tell)
- NEVER show exploratory analysis to stakeholders — concentrate on the pearls

### Who, What, How (in this order)

| Question | Detail |
|----------|--------|
| **Who** | Specific audience + your relationship with them. Narrow the audience — avoid "internal and external stakeholders." Identify the decision maker. |
| **What** | What must they know or DO? Always recommend an action. Even if uncertain, suggest possible next steps — gives audience something to react to. |
| **How** | Only AFTER who + what: what data supports your case? Data = supporting evidence. |

### Communication Mechanism Continuum

- **Live presentation** (left) — you control pacing, less detail needed on slides
- **Written document** (right) — audience controls, more detail needed
- **Slideument** — hybrid serving both; poses challenges for both needs

### Key Tools

- **3-minute story**: If you had 3 minutes, what would you say? Forces clarity.
- **Big Idea** (Duarte): A single sentence that (1) articulates your unique POV, (2) conveys what is at stake, (3) is a complete sentence.
- **Storyboarding**: Use Post-it notes or whiteboard BEFORE opening software. Easier to rearrange and discard without attachment.

### Context Questions Checklist

- What background information is relevant or essential?
- Who is the audience/decision maker? What do we know about them?
- What biases might make them supportive or resistant?
- What data strengthens our case? Is it familiar or new to them?
- Where are the risks that could weaken our case?
- What would a successful outcome look like?
- If you had one sentence, what would you say?

---

## Lesson 2: Choosing the Right Visual

### Decision Tree — When to Use What

| Visual Type | Use When |
|-------------|----------|
| **Simple text** | 1-2 numbers to communicate. Make the number BIG with supporting words. Do NOT put 1-2 numbers in a chart. |
| **Table** | Mixed audience seeking their own row; multiple units of measure. AVOID in live presentations. |
| **Heatmap** | Table + visual cues via colour saturation. Always include a legend. |
| **Line graph** | Continuous data (usually time). Single, two, or multiple series. Consistent intervals on x-axis are mandatory. |
| **Slopegraph** | Two time periods or comparison points. Shows absolute values + rate of change intuitively. |
| **Vertical bar** | Categorical data, single/two/multiple series. More series = harder to read. |
| **Stacked vertical bar** | Compare totals + subcomponents. Hard to compare non-bottom series. Use sparingly. |
| **Waterfall chart** | Starting point → increases → decreases → ending point. |
| **Horizontal bar** | **Go-to for categorical data.** Easy to read: labels left-to-right, eyes hit category names before data (z-pattern). |
| **Stacked horizontal bar** | Parts of whole, negative-to-positive scale (e.g., Likert survey data). |
| **100% stacked bar** | Proportions summing to 100%. Consider also showing absolute totals. |
| **Square area graph** | Only for numbers of vastly different magnitudes. Avoid all other area graphs. |
| **Scatterplot** | Relationship between two variables. Encode data on x and y simultaneously. |

### Visuals to AVOID

| Avoid | Why |
|-------|-----|
| **Pie charts** | Humans cannot accurately compare angles/areas. Even with labels, not worth the space. Replace with horizontal bar chart sorted by value. |
| **Donut charts** | Even worse — comparing arc lengths is harder than angles. |
| **3D charts** | NEVER use 3D. Skews perception, adds chart junk (side/floor panels). Only exception: actually plotting a third dimension. |
| **Secondary y-axis** | Confusing — audience must figure out which data maps to which axis. Alternatives: (1) label second series directly, (2) pull into separate graph sharing the same x-axis. |

### Critical Rules

- **Bar charts MUST have a zero baseline** — violating this creates false visual comparison (Fox News example: 460% visual increase vs 13% actual)
- **Line graphs CAN have nonzero baselines** — but make it clear and don't overzoom
- **Bar width** should be wider than white space between bars, but not so wide audience compares areas
- **Consistent time intervals** on x-axis for line graphs — never mix decades with years
- **Logical category ordering**: natural order if it exists; otherwise biggest-first or smallest-first depending on emphasis

---

## Lesson 3: Eliminate Clutter

### Cognitive Load Principle

- Every element on the page costs the audience brain power
- **Perceived** cognitive load matters most — if it LOOKS hard, audience gives up
- Maximise the **data-ink ratio** (Tufte): larger share of ink devoted to data = better
- Maximise **signal-to-noise ratio** (Duarte): signal = message, noise = clutter

### The 6 Gestalt Principles (Applied to Charts)

| Principle | Rule | Chart Application |
|-----------|------|-------------------|
| **Proximity** | Close objects = same group | Use spacing in tables to guide eyes to rows or columns |
| **Similarity** | Same colour/shape/size = related | Colour rows to guide reading direction; no borders needed |
| **Enclosure** | Objects in same area = group | Light background shading to separate forecast from actual |
| **Closure** | Brain fills in gaps | Remove chart borders and background — graph still reads as cohesive |
| **Continuity** | Eyes seek smoothest path | Remove y-axis line — consistent white space still aligns bars |
| **Connection** | Connected objects = group | Line graphs leverage this — lines create order in data |

### Decluttering Step-by-Step (the 6 Moves)

1. **Remove chart border** — use white space instead (closure principle)
2. **Remove gridlines** — if kept, make thin and light grey; never compete with data
3. **Remove data markers** — only use with purpose, not as default
4. **Clean up axis labels** — remove trailing zeros, abbreviate months to fit horizontally, eliminate diagonal text
5. **Label data directly** — eliminate legend; leverage proximity principle
6. **Use consistent colour** — label text same colour as its data series (similarity principle)

### Alignment Rules

- **Left-justify text** (avoid centre-aligned — creates no clean lines)
- **Upper-left-most justify** titles, axis titles, legends — audience sees how to read before reaching data
- Avoid **diagonal elements** — diagonal text is 52% slower to read (45°) and 205% slower at 90°
- Create clean vertical and horizontal lines of elements and white space

### White Space Rules

- Margins must remain free of text and visuals
- Do NOT stretch visuals to fill available space
- NEVER add data just to fill space
- White space = dramatic pause in a presentation — strategically powerful
- If one thing is really important, make it the ONLY thing on the page

### Contrast Rule

- "Easy to spot a hawk in a sky full of pigeons, but as variety of birds increases, the hawk becomes harder to find" (Ware)
- The more things we make different, the less any single thing stands out
- Make the ONE important thing very different from everything else

### Keep These Redundant Details

- Dollar signs ($), percent signs (%), commas in large numbers — always retain with data
- These ease interpretation even if title already states the unit

---

## Lesson 4: Focus Attention — Preattentive Attributes

### How Vision Works

- **Iconic memory**: fraction-of-a-second processing, tuned to preattentive attributes
- **Short-term memory**: holds ~4 chunks — legend with 10 colours = cognitive overload
- **Long-term memory**: visual + verbal combined trigger strongest recall

### The Preattentive Attributes (Adapted from Few)

Orientation | Shape | Line length | Line width | Size | Curvature | Added marks | Enclosure | Hue | Intensity | Spatial position

### Quantitative vs Categorical

- **Quantitative encoding**: line length, spatial position, line width, size, intensity (longer = greater)
- **Categorical encoding**: colour hue, shape — NOT quantitative (red is not "more" than blue)

### Two Strategic Uses

1. **Direct attention** — make the audience see what you want BEFORE they consciously think
2. **Create visual hierarchy** — establish implicit order for processing information

### The "Where Are Your Eyes Drawn?" Test

- Create your visual → close eyes → look back → note where eyes land first
- Better: show colleague and have them narrate what they see and in what order

### Rules for Using Preattentive Attributes

- **3-8 seconds**: studies show we have this window before audience decides to engage or move on
- Use preattentive attributes so that even in 3 seconds, the gist comes through
- **Push everything to background first** (grey), then make explicit choices about what to bring forward
- Data labels: use sparingly as "look here" signals, not on every data point

### Size

- Relative size = relative importance
- If 3 things are equally important, size them the same
- If one thing is most important, make it BIG
- Don't let layout accidents (e.g., placeholder sizing) signal false importance

### Colour — The Most Powerful Attribute

**Core approach**: Design in shades of grey, pick ONE bold colour to draw attention.

| Rule | Detail |
|------|--------|
| **Base colour = grey, not black** | Grey allows greater contrast when bold colour appears |
| **Default highlight = blue** | (1) No colourblindness issues, (2) prints well in B&W, (3) versatile |
| **Use sparingly** | Too many colours = rainbow land = nothing stands out |
| **Use consistently** | Same colour = same meaning throughout. A change in colour signals change in topic/tone. |
| **Colourblind safe** | ~8% of men are red-green colourblind. Avoid red+green together. Use blue (positive) + orange (negative). Add bold/plus/minus signs as backup cues. |
| **Tone-appropriate** | Bold black for clinical/serious; muted blue for friendly; peppy colours for lighthearted content |
| **Brand colours** | Use 1-2 brand colours as "look here" cues; keep rest muted grey. If brand colour lacks contrast, use a different standout colour. |
| **Heatmap over rainbow** | Single-colour saturation scale (heatmap) beats rainbow — carries quantitative connotation |
| **Dark backgrounds** | Reverse the logic: grey baseline, white stands out. Yellow pops against black. Generally avoid dark backgrounds. |

### Position on Page

- Audience starts **top-left**, scans in **z-pattern** zigzags
- Put the most important thing at the **top**
- On slides: action title at top = main takeaway
- In data: consider whether reordering data to put key insight at top makes sense
- Never make audience read bottom-right to top-left

---

## Lesson 5: Think Like a Designer

### Four Design Principles

#### 1. Affordances (from product design)

- Visual cues that indicate how to interact with the visualisation
- Three sub-rules: **highlight important stuff**, **eliminate distractions**, **create clear hierarchy**
- **10% rule**: highlight at most 10% of the visual design (Lidwell et al.)

**Highlighting techniques ranked:**
- **Bold** — preferred: minimal noise, clearly highlights
- *Italics* — minimal noise but less standout, less legible
- Underline — adds noise, compromises legibility, use sparingly
- UPPERCASE — works for titles/labels/keywords (short sequences)
- **Colour** — effective when used sparingly, best combined with bold
- **Size** — signals importance
- **Inversing** — effective but noisy, use sparingly
- Layering multiple attributes (large + coloured + bold) for highest-priority items

#### 2. Accessibility

- "If it's hard to read, it's hard to do" (Song & Schwarz, 2008) — fussy fonts made students judge exercise routines as harder
- **Make it legible**: consistent, easy-to-read font
- **Keep it clean**: leverage visual affordances
- **Straightforward language**: simple > complex, fewer words > more, spell out acronyms
- **Remove unnecessary complexity**: when choosing between simple and complicated, favour simple
- **Text is your friend**: every chart needs a title, every axis needs a title (exceptions are extremely rare)
- **Action titles** on slides: "Estimated 2015 spending is above budget" beats "2015 Budget"
- **Annotations**: few choice words on a graph dramatically accelerate understanding

#### 3. Aesthetics

- More aesthetic designs are perceived as easier to use (whether they are or not)
- Aesthetic designs promote creative thinking, foster positive relationships, increase tolerance of problems
- Three aesthetic priorities: **smart colour**, **proper alignment**, **leveraged white space**

#### 4. Acceptance

- Strategies for resistant audiences:
  - Articulate benefits of the new approach
  - Show side-by-side comparison (old vs new)
  - Provide multiple options and seek input
  - Get a vocal audience member on board first

---

## Lesson 6: Tell a Story

### Why Story Works

- Stories engage emotion in ways facts cannot (McKee, HBR)
- Red Riding Hood test: 80-90% of adults recall the high-level story — proof of story's memory power
- Conventional rhetoric (bullet-point facts) = intellectual only; story = emotional + intellectual

### Aristotle's Three-Act Structure Applied to Data

| Act | Content | Data Presentation Equivalent |
|-----|---------|------------------------------|
| **Beginning** (Setup) | Setting, main character, imbalance, desired balance | Context: who is the audience (they are the hero), what changed, what should happen |
| **Middle** (Conflict) | Protagonist faces escalating challenges | Supporting data, comparison points, options, benefits of recommendation |
| **End** (Resolution) | Climax + dramatic question answered | Clear call to action; tie back to the beginning |

### Story Construction Questions (McKee)

- What does the protagonist want to restore balance?
- What is the core need?
- What keeps them from achieving their desire?
- How would they act in the face of antagonistic forces?

### Conflict and Tension Are Essential

- A story where everything is rosy is not attention-grabbing
- Frame in terms of the audience's problem — they have a stake in the solution
- Duarte: tension = "the conflict between what is and what could be"

### Narrative Structure

**Order options:**
- **Chronological**: take audience through your analytical journey. Works when you need to establish credibility or audience cares about process.
- **Lead with the ending**: start with call to action, then back into supporting evidence. Works when trust exists and audience wants the "so what."

**Bing, Bang, Bongo** (repetition framework):
1. Tell them what you will tell them (executive summary)
2. Tell them (main content)
3. Tell them what you told them (recap + call to action)

### Spoken vs Written Narrative

- **Live**: words on screen reinforced by spoken words; keep slides sparse so audience listens
- **Written**: must stand alone; make "so what" explicit on every slide/section
- Tell audience your presentation structure upfront ("I will start with X, then cover Y")

### Four Tactics for Story Clarity

1. **Horizontal logic** — slide titles alone tell the overarching story (requires action titles)
2. **Vertical logic** — everything on one slide self-reinforces (title ↔ visual ↔ text)
3. **Reverse storyboarding** — flip through final deck, write down each slide's main point; result should match your intended storyboard
4. **Fresh perspective** — show to someone without context; have them narrate what they see

### Vonnegut's Writing Rules (Applied to Data)

1. Find a subject you care about
2. Do not ramble
3. Keep it simple
4. Have the guts to cut
5. Sound like yourself
6. Say what you meant to say
7. Pity the readers — be a sympathetic, patient teacher

---

## Case Study Patterns

### Spaghetti Graph Solutions (Too Many Overlapping Lines)

1. **Emphasise one line at a time** — bold + colour one series, grey the rest
2. **Separate spatially (vertically)** — same x-axis, one mini-graph per series (sparklines)
3. **Separate spatially (horizontally)** — same y-axis, side-by-side mini-graphs (small multiples)
4. **Combined approach** — separate AND emphasise one at a time
5. **Reduce data** — do you really need all categories/years?

### Pie Chart Alternatives

1. **Simple text** — if 1-2 numbers tell the story, just state them
2. **Simple bar graph** — aligned baseline, easy comparison
3. **100% stacked horizontal bar** — preserves part-to-whole, consistent baselines on both ends
4. **Slopegraph** — shows change between two points with intuitive slope

### Animation Strategy (Presentation vs Circulation)

- **Live presentation**: build the graph progressively using animation (Appear/Disappear only — no fly-ins)
- **Circulated version**: single annotated visual with all key points marked
- Stack all animation frames on one slide; final annotated version on top for print

### Logic in Order

- When telling multiple stories from one dataset, preserve the same category order throughout
- Rearranging data between views creates mental tax
- Use colour to highlight different stories while keeping order stable

---

## Model Visual Checklist

Apply this checklist to every data visualisation before sharing:

- [ ] **Context**: Can I state in one sentence who this is for and what they should do?
- [ ] **Visual type**: Is this the easiest-to-read chart type for this data and message?
- [ ] **Zero baseline**: If bar chart, does y-axis start at zero?
- [ ] **No 3D**: Is the chart free of 3D effects?
- [ ] **No pie/donut**: Have I avoided pie and donut charts (or justified their use)?
- [ ] **Chart border removed**: No unnecessary box around the chart?
- [ ] **Gridlines**: Removed or made thin light grey?
- [ ] **Data markers**: Only present with purpose, not by default?
- [ ] **Axis labels**: Clean (no trailing zeros, no diagonal text)?
- [ ] **Direct labels**: Data series labelled directly (no distant legend)?
- [ ] **Colour strategy**: Grey base + one bold colour for emphasis?
- [ ] **Colourblind safe**: Avoided red+green together? Added backup cues?
- [ ] **Alignment**: Left-justified text, upper-left titles, clean vertical/horizontal lines?
- [ ] **White space**: Margins preserved, visuals appropriately sized?
- [ ] **Titles**: Graph title and all axis titles present?
- [ ] **Action title**: Title states the "so what," not just a description?
- [ ] **Annotations**: Key insights called out directly on the visual?
- [ ] **Visual hierarchy**: "Where are your eyes drawn?" test passed?
- [ ] **Story**: Does this visual support a clear beginning-middle-end narrative?
- [ ] **Call to action**: Is it obvious what the audience should know or do?

---

## Anti-Patterns Summary

| Anti-Pattern | Fix |
|-------------|-----|
| Showing all 100 oysters (exploratory dump) | Show only the 2 pearls (explanatory) |
| Pie/donut chart | Horizontal bar chart or simple text |
| 3D anything | Flat 2D always |
| Rainbow colours | Grey + one accent colour; heatmap for scales |
| Legend far from data | Label data directly |
| Centre-aligned text | Left-justify |
| Diagonal axis labels | Abbreviate or switch to horizontal bar |
| Every data point labelled | Label only the points that matter |
| No chart/axis titles | Always title the chart and every axis |
| Descriptive title ("Q3 Revenue") | Action title ("Q3 revenue exceeded target by 12%") |
| No call to action | Always end with what audience should do |
| Secondary y-axis | Label directly or split into two graphs |
| Dark/coloured background | White background (unless brand requires otherwise) |
| Filling every pixel of space | Preserve white space — it is strategic |
| Same visual for presentation + report | Build progressively for live; annotate fully for circulation |

---

## References

- Knaflic, Cole Nussbaumer. *Storytelling with Data.* Wiley, 2015.
- Tufte, Edward. *The Visual Display of Quantitative Information.* Graphics Press, 2001.
- Few, Stephen. *Show Me the Numbers.* Analytics Press, 2004.
- Duarte, Nancy. *Resonate.* Wiley, 2010.
- Lidwell, Holden, Butler. *Universal Principles of Design.* Rockport, 2010.
- Ware, Colin. *Information Visualization: Perception for Design.* Morgan Kaufmann, 2004.
- Atkinson, Cliff. *Beyond Bullet Points.* Microsoft Press, 2011.