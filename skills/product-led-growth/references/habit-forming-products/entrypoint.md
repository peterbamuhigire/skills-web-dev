---
name: habit-forming-products
description: Use when designing products, features, or onboarding flows that need
  to build unprompted repeat engagement — daily/weekly return without ads or reminders.
  Covers the Hook Model (Trigger → Action → Variable Reward → Investment), internal
  trigger...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Habit-Forming Products — The Hook Model
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing products, features, or onboarding flows that need to build unprompted repeat engagement — daily/weekly return without ads or reminders. Covers the Hook Model (Trigger → Action → Variable Reward → Investment), internal trigger...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `habit-forming-products` or would be better handled by a more specific companion skill.
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
| UX quality | Habit loop assessment | Markdown doc covering Hooked-model trigger, action, variable reward, and investment per feature | `docs/product/habit-loop-assessment.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Grounded in Eyal, N. & Hoover, R. (2014). *Hooked: How to Build Habit-Forming Products.*

A **habit** is a behaviour done with little or no conscious thought. Habit-forming products attach to users' internal triggers and become the automatic response to an emotional state — without advertising, push prompts, or friction.

## When to Use

Load this skill when:
- Designing daily/weekly engagement loops for apps, SaaS, or mobile
- Evaluating why users are not returning unprompted
- Designing onboarding that turns first-time users into devotees
- Deciding whether to invest in gamification vs. genuine habit formation

**Not every product needs habits.** Life insurance, once-a-year tax tools, and high-price B2B purchases do not require habitual users. Habits are essential only for products where ongoing, unprompted engagement drives business value (SaaS retention, social networks, content apps, productivity tools).

---

## The Habit Zone

Before designing hooks, verify your product belongs in the Habit Zone:

```
Habit Zone = High Frequency × High Perceived Utility
```

- **Frequency threshold:** Users must engage at least weekly. Monthly is too infrequent to form a habit.
- **Perceived utility:** Users must feel genuine value, not merely enjoy novelty.
- **The 9× Rule:** To displace an entrenched habit, a new product must be approximately 9× better — because users irrationally overvalue existing routines. Marginally better is not enough.
- **Painkiller vs. Vitamin:** Habit-forming products must solve a real, frequent pain (painkiller). "Nice-to-have" products (vitamins) rarely cross the Habit Zone.

**Business value of habits:**
- Higher Customer Lifetime Value (CLTV)
- Price insensitivity (habitual users tolerate price increases)
- Viral Cycle Time compression — daily users invite more, respond faster
- Competitive moat: switching costs increase with each investment cycle

---

## Habit Discovery — Finding the Opportunity

Before designing hooks, confirm a genuine habit-forming opportunity exists. Four sources:

1. **Look in the Mirror** — The most reliable starting point (Paul Graham): identify a problem you experience yourself. Founders who solve their own pain point are the users they understand most deeply. Warning: the further you are from your past self, the lower your odds of success — you cannot manufacture empathy.

2. **Nascent Behaviors** — Watch small, niche groups doing new things that could scale. Early adopters reveal mass-market needs before mass-market awareness exists. Things that looked like toys have become essential: cameras as "child's toys" (1900s), phones as "toys for the rich" (1870s), personal computers (1970s). Dismissed nascent behaviors are often the most valuable signals.

3. **Enabling Technologies** — New infrastructure creates new Hook cycle possibilities. Follow the three-phase wave: infrastructure (networks, hardware) → enabling technologies (APIs, platforms) → high-penetration applications (consumer products). Identify where new infrastructure makes Hook cycles faster, more frequent, or higher-reward.

4. **Interface Changes** — Major UI innovations unlock new habit surfaces. GUI replaced terminal. Mobile camera replaced standalone cameras. Infinite scroll replaced paginated feeds. Each shift created entirely new habit opportunities. Anticipate the next interface layer (wearables, ambient computing, spatial computing) and build for those interaction primitives.

---

## The Hook Model

Four phases, cycled repeatedly until the habit is formed:

```
Trigger → Action → Variable Reward → Investment → [loads next Trigger]
```

---

## Phase 1: Trigger

A trigger is the cue that initiates behaviour. There are two types:

### External Triggers
Information placed in the user's environment telling them what to do next.

| Type | Description | Use |
|------|-------------|-----|
| **Paid** | Ads, SEM, promoted content | New user acquisition only — unsustainable for re-engagement |
| **Earned** | Press, viral videos, app store featuring | Short-lived; hard to sustain |
| **Relationship** | Word of mouth, referrals, social shares | Powerful for viral growth; requires engaged users |
| **Owned** | App icon, email newsletter, push notification | The most valuable for repeat engagement; requires user opt-in |

**Owned triggers are the goal.** They occupy real estate in the user's environment and fire consistently.

### Internal Triggers
Emotional associations stored in memory that cue the behaviour automatically. No external prompt needed.

**Key insight:** Negative emotions are the most powerful internal triggers.
- Boredom → opens Twitter/TikTok
- Loneliness → opens Facebook/Instagram
- Uncertainty → opens Google
- Fear of missing a moment → opens camera/Instagram
- Fear of falling behind → opens email

**Designing for internal triggers — the 5 Whys method:**
Ask "Why?" five times to drill from the feature level to the emotional root.

```
Why does Julie use email?
→ To send and receive messages.
Why does she want that?
→ To share and receive information quickly.
Why does she want that?
→ To know what's happening with people around her.
Why does she need to know?
→ To know if someone needs her.
Why does she care?
→ She fears being out of the loop.  ← Internal trigger: fear
```

**Template:** "Every time the user [internal trigger], he/she [intended behaviour]."
Example: *Every time Jenny feels bored, she opens the Facebook app.*

**Goal:** Move users from external → internal triggers over repeated cycles. A well-hooked user acts without any prompt.

---

## Phase 2: Action

The simplest behaviour in anticipation of a reward. If the trigger fires but action doesn't follow, the trigger is wasted.

### Fogg Behaviour Model: B = MAT

```
Behaviour occurs when Motivation + Ability + Trigger are all present simultaneously.
```

If any element is missing or insufficient, the action line is not crossed.

### Core Motivators (what drives motivation)
1. **Pleasure / Pain** — seek pleasure, avoid discomfort
2. **Hope / Fear** — optimism about outcomes vs. anxiety about risk
3. **Social Acceptance / Rejection** — belonging vs. exclusion

### 6 Elements of Simplicity (what limits ability)
Identify the user's scarcest resource at the moment of action and remove that friction.

| Element | Question to ask |
|---------|----------------|
| **Time** | Can they do this in under 10 seconds? |
| **Money** | Is there a cost barrier? |
| **Physical effort** | Too many taps, scrolls, or steps? |
| **Brain cycles** | Is the decision too complex to make quickly? |
| **Social deviance** | Does this feel weird or embarrassing to do? |
| **Non-routineness** | Is this too different from their existing habits? |

**Critical rule: Increase ability before motivation.** Reducing friction is cheaper, faster, and more effective than persuasion. Make action so easy that users already know how to do it.

### Action Design Patterns
- **Single clear CTA** — one path, no competing choices (Hick-Hyman Law)
- **Social login** — eliminate registration friction
- **One-click/one-tap actions** — Twitter's retweet button, Facebook Like
- **Infinite scroll** — removes the pause-and-click barrier
- **Progressive disclosure** — start with the simplest version; reveal complexity later

### Persuasion Heuristics (Action-Phase Amplifiers)

Four mental shortcuts that increase the probability of crossing the action line without increasing friction:

| Heuristic | Mechanism | Application |
|-----------|-----------|-------------|
| **Scarcity Effect** | Perceived scarcity raises perceived value; abundance decreases it | "Only 14 left in stock", limited-time access, early-adopter pricing. Warning: false scarcity damages trust when discovered. |
| **Framing Effect** | Context and presentation change perceived value independently of objective quality | Same product commands different response in premium vs. commodity framing. Research: identical wine tastes better — and registers higher brain activation — when priced higher. |
| **Anchoring Effect** | The first number seen sets a reference point; all subsequent judgements are relative to it | Show full price before discount; sequence pricing tiers from highest to lowest; early numbers anchor the frame. |
| **Social Proof & Authority** | Majority behavior signals safety; authority figures signal correctness | Testimonials, expert endorsements, "X users already joined", bestseller badges. Research base: Bandura's Social Learning Theory — people adopt behaviors they observe in others like themselves or in role models. |
| **Endowed Progress Effect** | People assigned artificial head-start progress toward a goal are significantly more motivated to complete it than those who start from zero — even when the total work required is identical | Pre-fill Step 1 of onboarding so users feel already started; LinkedIn-style profile strength meters begin at "Beginner" not 0%; pre-punched loyalty cards (2 of 10 already stamped) increase completion 82% vs blank cards (Nunes & Drèze, 2006). This exploits the Goal-Gradient Effect: proximity to a goal accelerates effort. |

These heuristics operate at the System 1 level (see `ux-psychology`). They work because users are making decisions quickly, with incomplete information, under low attention. They do not replace good design — they amplify it.

---

## Phase 3: Variable Reward

The reward that resolves the user's craving — but with variability.

**Key neuroscience:** Dopamine surges in *anticipation* of reward, not from the reward itself. Variability amplifies this — the brain stays in a seeking state when outcomes are uncertain. Predictable rewards lose power; variable ones sustain it.

### Three Types of Variable Reward

| Type | Driver | Examples |
|------|--------|---------|
| **Tribe** | Social validation, acceptance, status | Likes, comments, upvotes, follower counts, reputation badges |
| **Hunt** | Information and resource acquisition | Social feeds, newsfeeds, search results, slot machines, bargain shopping |
| **Self** | Mastery, completion, competence | Progress bars, streaks, skill levels, "Day Complete" screens, achievements |

Most powerful products use **two or three types simultaneously.**

### Reward Design Rules
- **Satisfy the craving but leave wanting more** — the reward must feel complete yet open-ended
- **Variability must feel fair** — random must not feel rigged; users must feel agency
- **Autonomy preserves engagement** — users who feel controlled lose intrinsic motivation; give meaningful choices within the variable loop

### Finite vs. Infinite Variability

The distinction determines long-term sustainability of engagement:

**Finite variability** — the reward pool is known or bounded. Users eventually map all outcomes. Dopamine response flattens. Engagement declines. Classic slot machines with disclosed RTP schedules, single-player games with fixed enemy patterns, and achievement systems with finite badge sets all exhibit this decay.

**Infinite variability** — the outcome space cannot be exhausted. Social feeds (content from millions of humans), open-world games, search results, and user-generated content platforms all maintain unpredictability indefinitely because the source of variability is unbounded (other people, the real world, new content).

**Design rule:** Where possible, source variability from humans and real-world events rather than from system-generated outcomes. The internet of other people is the most powerful variable reward engine ever built. Build interfaces that tap it.

---

## Phase 4: Investment

The user does a small "bit of work" that increases the value of the product for future use. Unlike action (which is for immediate reward), investment is for *future* benefit.

**Four psychological mechanisms make investment sticky:**

1. **IKEA Effect** — People irrationally overvalue things they helped create. Users value a product more because they built part of it (playlists, profiles, annotations).
2. **Consistency bias** — Past behaviour predicts future behaviour. A small first commitment leads to larger future commitments.
3. **Cognitive dissonance avoidance** — Users rationalise that something they've invested in must be valuable.
4. **Reciprocation** — Humans evolved to reciprocate value received, and this applies to non-human systems. Stanford research: participants who received help from a computer completed nearly 2× more work for it in a subsequent task than those who had not. Implication: deliver genuine value *before* asking for investment, not after. The product must earn the right to ask.

### What Users Invest (Stored Value)

| Type | Examples |
|------|---------|
| **Content** | Playlists, posts, saved items, notes, photos |
| **Data** | Preferences, history, settings, linked accounts |
| **Followers/connections** | Social graph, subscriber lists |
| **Reputation** | Points, badges, rankings, reviews |
| **Skill** | Learned workflows, shortcuts, customised environments |

Each investment increases switching cost and makes the product harder to abandon.

### Critical timing rule
**Ask for investment AFTER the variable reward, not before.**
Users who just received a reward are primed to reciprocate. Investment requested before reward creates friction and resistance.

### Investment loads the next trigger
Every bit of work a user does should produce a cue that brings them back.
- Following a user on Twitter → future tweet notifications
- Adding a contact in a CRM → follow-up reminders
- Completing a reading plan day → next day's notification loads

---

## Ethics: The Manipulation Matrix

Before building a Hook, evaluate where you stand.

Ask two questions:
1. **Would you use this product yourself?**
2. **Does this product materially improve users' lives?**

| | Improves lives: Yes | Improves lives: No |
|---|---|---|
| **Use it yourself: Yes** | **Facilitator** ✅ Best position | **Entertainer** ⚠️ Ephemeral |
| **Use it yourself: No** | **Peddler** ⚠️ Lacks empathy | **Dealer** ❌ Exploitation |

**Facilitator:** You use the product; you believe it genuinely helps users. This is the only position with both high ethical standing and high probability of success. Facilitators understand their users because they *are* their users.

**Peddler:** Altruistic intent but no personal connection to the problem. Peddlers cannot truly understand users they've never been. Success rate is low; designs feel hollow.

**Entertainer:** You use it; it's fun but not life-improving. Entertainment is valuable but ephemeral — hits-driven, not habit-driven. Requires a constant pipeline of novelty.

**Dealer:** Neither use it nor believe it helps. Building purely to extract value from users. Lowest long-term success; highest ethical risk.

**Obligation:** Designers of habit-forming products must identify users forming unhealthy dependencies and have procedures to help them. The ~1% who form pathological attachments cannot be dismissed.

---

## Habit Testing

Use this 3-step cycle after your product is live.

### Step 1: Identify
Define what a "habitual user" looks like for your product. Be realistic — not all products warrant daily use.
- Social apps: multiple times daily
- Productivity tools: daily
- Reference tools: 2–3× per week

Find users who meet this threshold. If fewer than 5% of users are habitual, the product likely has a fundamental problem — wrong users or wrong design.

### Step 2: Codify
Find the **Habit Path** — the series of actions that habitual users consistently take that non-habitual users don't.

> Twitter found: users who followed ≥30 accounts hit a tipping point that dramatically increased long-term retention.

Use cohort analysis to identify which specific early actions predict long-term devotion.

### Step 3: Modify
Redesign onboarding and early flows to guide *all* new users down the Habit Path.

This is a continuous process — run it with every major product iteration.

### Habit Testing Benchmarks

Use these as diagnostic thresholds:

| Signal | Threshold | Interpretation |
|--------|-----------|----------------|
| Habitual users in cohort | `< 5%` | Fundamental problem: wrong users or wrong Hook design |
| App abandoned after single use | `26%` of installs (2010 baseline) | Normal attrition; watch for outliers above this |
| Time to first check after waking | `79%` within 15 minutes | Benchmark for "owned trigger" strength on mobile |
| Twitter retention tipping point | Following `≥ 30` accounts | Example of a concrete Habit Path threshold — find yours |

When you find your product's equivalent of "following 30 accounts", that threshold becomes the target your onboarding must drive users toward.

---

## Workbook Application Framework

The Supplemental Workbook (Eyal & Hoover, 2014) provides a structured 8-exercise sequence for applying the Hook Model to a real product. Work through these in order — they build on each other.

**Exercise 1 — Foundation**
1. Select the product or feature to make habit-forming.
2. State why the business model requires a habit (retention, frequency, switching cost).
3. Describe the problem users are solving with it today.
4. Identify current solutions and why they are inadequate.
5. Define the intended habitual behaviour.
6. Specify expected engagement frequency — must be at least weekly or habit formation is very difficult.

**Exercise 2 — Triggers**
1. Name a single real target user (not a persona archetype — an actual person).
2. Describe what that user is doing immediately before the behaviour.
3. Apply the 5 Whys to find 3 internal trigger candidates.
4. Identify the most frequent internal trigger from those 3.
5. Write the trigger sentence: "Every time [user] feels [internal trigger], they [intended behaviour]."
6. Identify the 3 best places/moments to fire an external trigger.
7. Brainstorm 3 conventional external trigger methods + 3 unconventional ones.

**Exercise 3 — Action**
1. Count every step between internal trigger and completed action.
2. Compare step count to the leading competitor.
3. Identify which of the 6 simplicity elements (time, money, effort, brain cycles, social deviance, non-routine) is limiting the user most.
4. Brainstorm 3 ways to remove that specific friction.
5. Identify which persuasion heuristics (Scarcity, Framing, Anchoring, Social Proof) could increase action likelihood at each step.

**Exercise 4 — Variable Reward**
1. Interview at least 5 users about the most enjoyable or encouraging moment in the product.
2. Identify the moments of delight and surprise they describe.
3. Determine which outcome most directly alleviates the internal trigger identified in Exercise 2.
4. Brainstorm reward enhancements for each of the 3 reward types (Tribe, Hunt, Self).

**Exercise 5 — Investment**
1. Identify the single "bit of work" most likely to increase the user's return probability.
2. Brainstorm 3 investments that both load the next trigger AND store value (content, data, connections, reputation, or skill).
3. Estimate the delay between the investment and when the loaded trigger fires.
4. Identify how to reduce that delay.

**Exercise 6 — Ethics**
1. Do you personally use this product? (Yes/No)
2. Does it materially improve users' lives? (Yes/No)
3. Assign your quadrant (Facilitator / Peddler / Entertainer / Dealer).
4. If not Facilitator: identify what must change before proceeding.

**Exercise 7 — Habit Testing**
1. State the frequency threshold that defines a habitual user (from Exercise 1, Q6).
2. Calculate the % of users who meet that threshold in the last 60 days.
3. Describe what is unique about habituated users vs. non-habituated users.
4. Redesign the onboarding path so all users encounter the actions that habituated users took.

**Exercise 8 — Observation**
1. Spend one week logging products you use habitually.
2. For each: what triggered you (external/internal)? How could it be easier? More frequent? More rewarding? How does it solicit investment?
3. Note any product used in an unintended way — these nascent behaviors are signals.
4. Observe target users of your own product for workarounds and adaptations they have invented.

---

## Habit Design Checklist

Before shipping any feature intended to build repeat engagement:

**Discovery**
- [ ] Confirmed a genuine habit-forming opportunity exists (one of the 4 discovery methods)
- [ ] Verified product belongs in the Habit Zone (weekly+ frequency, real pain)

**Trigger**
- [ ] Identified the specific internal trigger (emotional root via 5 Whys)
- [ ] Owned external trigger is in place (push notification, icon, email)
- [ ] External trigger fires closest to when the internal trigger is likely to occur

**Action**
- [ ] Counted steps from trigger to reward — fewer is always better
- [ ] Identified the scarcest resource and removed that friction
- [ ] Reduced choices to a single clear path (Hick-Hyman Law)
- [ ] Identified which persuasion heuristics apply at this action step

**Variable Reward**
- [ ] Reward satisfies the craving but leaves the user wanting more
- [ ] At least one of Tribe, Hunt, or Self reward types is in play
- [ ] Variability is infinite or sourced from unpredictable human behavior
- [ ] Variability feels fair and maintains user agency

**Investment**
- [ ] Value delivered BEFORE investment is requested (reciprocation principle)
- [ ] Investment is asked AFTER the variable reward
- [ ] Investment stores value (content, data, followers, reputation, or skill)
- [ ] Investment loads a trigger for the next cycle

**Ethics**
- [ ] Confirmed position on Manipulation Matrix (Facilitator quadrant)
- [ ] Product materially improves users' lives
- [ ] No dark patterns or manufactured false urgency

---

## Anti-Patterns

| Anti-Pattern | Problem |
|---|---|
| Extrinsic-only gamification (badges, points) | Collapses when rewards stop; no intrinsic hook |
| Asking for investment before reward | Creates resistance; users quit before investing |
| Fixed reward schedule | Predictable rewards lose power quickly; variability is the mechanism |
| Vitamin positioning | Nice-to-have products rarely cross the Habit Zone |
| Ignoring internal triggers | External triggers only work until users stop opening the notification |
| Being a peddler | Building for users you don't understand produces products users don't want |
| Notification spam | Destroys trust; users disable and eventually uninstall |

---

## Cross-References

- **`ux-psychology`** — cognitive science foundations: IKEA effect, goal-gradient, loss aversion, dual-process model, Hick-Hyman Law
- **`lean-ux-validation`** — validate your internal trigger hypothesis with real users before building
- **`ux-for-ai`** — when the habit-forming product involves AI features (trust, autonomy, transparency)
- **`interaction-design-patterns`** — Tidwell's behavioural patterns for the action and reward phases

---

## Sources

- Eyal, N. & Hoover, R. (2014). *Hooked: How to Build Habit-Forming Products.* Portfolio/Penguin.
- Eyal, N. & Hoover, R. (2014). *Hooked: Supplemental Workbook.* NirAndFar.com.
- Fogg, B.J. (2009). *A Behavior Model for Persuasive Design.* Persuasive Technology Lab, Stanford.
- Ariely, D., Mochon, D., Norton, M. (2011). *The "IKEA Effect": When Labor Leads to Love.* Journal of Consumer Psychology.