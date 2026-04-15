# Territory Design

Territory design rewards or punishes reps before they do anything. Design for fairness, motion fit, and analytic clarity, then rebalance on a cadence.

## Options and when to use them

| Model | Best for | Pros | Cons |
|---|---|---|---|
| Round-robin | SMB transactional, inbound-heavy | Simplest, fair on volume | No account expertise, duplicates in outbound |
| Geographic | Field sales, time-zone-sensitive products | Clear ownership, travel logic | Uneven market density |
| Vertical (industry) | Specialised buyers (health, finance, retail) | Deep persona expertise, reusable content | Ramp is longer; shrinks TAM per rep |
| Named-account | Enterprise, ABM | Relationship depth, ABM alignment | Requires disciplined list curation |
| Segment (ARR band or employee count) | Mixed motion | Aligns to motion; clean metrics | Boundary disputes at the edges |
| Hybrid (e.g., geo + vertical) | Large orgs with >30 AEs | Combines strengths | Complex; only worth it at scale |

## Fair balancing criteria

When allocating territories, balance on as many of these as possible:

- **Pipeline potential** (TAM within the territory measured in ARR).
- **Existing pipeline/book value** (inherited deals and customers).
- **Quality density** (match to ICP, not just count).
- **Installed-base expansion** (existing customers in the patch).
- **Travel/logistics** (for field sales).

Rule of thumb: no rep should have a TAM (or book) more than 1.25x another rep on the same team. Larger gaps create systemic attainment gaps.

## Named-account design

For enterprise named-account lists:

- 50-100 accounts per AE for net-new enterprise.
- 20-40 for strategic accounts where expansion is the priority.
- List refresh once per year (or per planning cycle).
- Each account tagged with tier (A/B/C), primary contact, last-touch date, current stage if active.
- Hard rule: only one AE can own an account at a time. If a multinational appears in two AE territories, escalate to sales leadership within a week.

## Rebalancing cadence

- **Annual**: full rebalance aligned to fiscal year, quota setting, and capacity planning.
- **Quarterly**: small swaps for obvious imbalances (a rep with no inbound, a rep drowning in it).
- **Ad-hoc**: when a rep joins or leaves, when a major account changes segment, when a merger affects the list.

Publish rebalance rules before the cycle. If reps learn the rules after the change, you have damaged trust permanently.

## Handling transfers mid-cycle

Common rule: 50/50 split on in-flight opportunities, or the original AE keeps the deal through Closed Won if it is in Stage 4+ already. Either way, publish the rule in advance and apply it consistently.

For named accounts transferred mid-cycle:

- New AE inherits forward pipeline.
- Departing AE retains credit (for commission) on deals already Stage 4+ that close within 60 days.
- Any new opportunity started post-transfer belongs to the new AE.

## Worked example — mid-market US, 5 AEs

Goal: balanced, segmented by ARR band and geography.

```text
Total TAM: 8,000 target accounts, $200M addressable ARR
Team: 5 AEs, quota $1.5M each

AE1: West Coast, 1.6k accounts, $42M TAM
AE2: Central, 1.5k accounts, $38M TAM
AE3: East Coast North, 1.6k accounts, $40M TAM
AE4: East Coast South, 1.6k accounts, $40M TAM
AE5: Strategic (50 named), spread nationally, $40M TAM
```

TAM spread 38-42M — within 1.1x; acceptable. AE5's named list is curated to high-propensity strategic accounts across geographies.

## Territory quality checks (run pre-launch)

- Does every territory contain at least 3x quota in reachable TAM?
- Is installed-base value roughly balanced (for expansion reps)?
- Are there no orphaned accounts (too small for enterprise, too big for SMB)?
- Are geographic conflicts resolved (travel time, time-zone mismatch)?
- Are handoff rules (SDR-to-AE pairing) explicit for each territory?

## Cross-references

- `saas-business-metrics` — pipeline coverage and attainment distribution per territory.
- `subscription-billing` — billing entity / tax jurisdiction may dictate geographic boundaries.

## Anti-patterns

- "Pick your own accounts" — scrambles for vanity logos, orphans less obvious TAM.
- Not adjusting quota when TAM is smaller — attainment gap becomes a hiring and morale problem.
- Rebalancing silently — reps will infer favouritism.
- Letting the top rep hoard accounts "just in case" — freezes TAM out of play.
