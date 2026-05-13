---
name: premium-client-sales
description: Use when running a premium-priced sales conversation, qualifying a high-value buyer, defending price against discount pressure, handling objections (price, risk, timeline, staffing, technology, fit), curating proof for skeptical buyers, or designing the offer-and-next-step sequence for a complex deal. Encodes an ethical persuasion gate, the buyer trust chain, objection formulas, and discount discipline rules.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Premium Client Sales
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Preparing or running a sales conversation for a premium-priced offer where price will be questioned.
- Qualifying whether a prospect is the right fit before investing in a long pursuit.
- Defending price against discount pressure or designing scope-vs-price trade-offs.
- Handling objections without scripts: price, risk, timeline, staffing, technology, or fit.
- Curating proof (case studies, references, demos, audits) for a skeptical buyer.
- Designing the buyer trust chain from problem framing through follow-through.

## Do Not Use When

- The offer is a transactional, low-consideration purchase where buyer behaviour is impulse-driven.
- The work is post-sale delivery; use `customer-service-excellence` instead.
- The question is internal product strategy with no live buyer; use `product-discovery` instead.
- The buyer has already signed and you need onboarding language; use `customer-service-excellence`.

## Required Inputs

- Offer description, target buyer profile, and price band.
- Known buyer context: stated problem, decision process, alternatives considered, budget range.
- Any prior conversations, objections raised, and proof assets already shown.
- Constraints: ethical limits, regulated audiences, public-channel risk.

## Workflow

1. Run the **ethical persuasion gate** first. If any gate fails, stop and rework the offer or audience.
2. Confirm **fit** before discovery. A misfit prospect is not a discount candidate, it is a referral.
3. Walk the **sales conversation arc**: fit-check, discovery, impact quantification, decision-process mapping, method, proof, scope, price logic, next step.
4. Frame the offer through the **buyer trust chain**: problem, diagnosis, proof, method, risk-control, offer, next action, follow-through.
5. For each objection raised, pick the matching **objection formula**, never a script. The formula names the underlying concern, surfaces the buyer's real criterion, then offers a structured response.
6. If price pressure appears, **narrow scope before discounting**. Discount discipline is enforced by the rules in `references/premium-pricing-and-discount-discipline.md`.
7. Close on a **specific next step** with a calendar slot, named owner, and a written confirmation, not a vague "we'll be in touch".
8. Log the conversation outcome and any commitments. Feed signals to `continuous-improvement-system`.

## Quality Standards

- Every claim has visible proof or is removed.
- Price is defended by value, scope, risk reduction, and authority assets, never by personality.
- The buyer always knows the next concrete step, the deadline, and who owns it.
- No urgency tactic, scarcity claim, or social proof reference is used unless it is literally true.
- Discount, when granted, is paired with a scope reduction or commitment trade.
- The conversation produces a written summary that the buyer can forward to other decision-makers without distortion.

## Anti-Patterns

- Discounting to win the meeting rather than the deal.
- Pitching method before quantifying impact.
- Treating "I need to think about it" as the real objection rather than a stand-in for an unspoken concern.
- Using social proof from outside the buyer's category as if it were comparable.
- Closing on "let me know" instead of a calendar slot.
- Confusing rapport with qualification. Liking you is not buying from you.
- Lowering price without removing scope, deadline pressure, or risk allocation.

## Outputs

- A qualification verdict: pursue, refer, or decline, with the reason.
- A written discovery summary that mirrors the buyer's words back to them.
- A proof bundle matched to the buyer's specific risk profile.
- A priced proposal with scope tiers and explicit risk-control terms.
- A next-step commitment: date, owner, deliverable.
- An objection log feeding the improvement loop.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Premium opportunity qualification note | Markdown with fit score, buyer path, proof needs, and next step | `docs/sales/premium-opportunity.md` |
| Correctness | Discovery question plan | Markdown question bank mapped to value, risk, budget, and decision criteria | `docs/sales/discovery-plan.md` |
| Operability | Objection and pricing response log | Markdown table with concern, response, evidence, tradeoff, and follow-up | `docs/sales/objection-log.md` |

## References

- `references/sales-conversation-arc.md` for the nine-stage arc and stage-exit criteria.
- `references/ethical-persuasion-gate.md` for the truth, legitimate-interest, visible-risk, real-urgency, and vulnerable-audience checks.
- `references/objection-handling-formulas.md` for formulas covering price, risk, timeline, staffing, technology, and fit.
- `references/premium-pricing-and-discount-discipline.md` for the premium-rate justification framework and the discount-only-with-scope-cut rule.
- `references/buyer-proof-curation.md` for selecting case studies, references, demos, and audits matched to buyer risk.
- Use `customer-service-excellence` after the deal closes. Use `continuous-improvement-system` to feed win/loss patterns into strategy review.
<!-- dual-compat-end -->

## Ethical Persuasion Gate (must pass before pitching)

| Gate | Pass Test | Fail Action |
|------|-----------|-------------|
| Truth | Every claim has evidence on file. | Remove the claim. |
| Legitimate interest | The buyer would still pursue this if fully informed. | Restructure the offer. |
| Visible risk | Buyer can see what could go wrong and how it is bounded. | Add written risk terms. |
| Real urgency | Any deadline reflects an actual constraint, not a manufactured one. | Drop the deadline language. |
| Vulnerable-audience protection | If the buyer is distressed, time-pressured, or asymmetrically informed, slow the process and add cool-off space. | Add 24-hour reflection clause. |

## Buyer Trust Chain (the order, every time)

Problem -> Diagnosis -> Proof -> Method -> Risk-control -> Offer -> Next action -> Follow-through.

Skipping a link breaks the chain. Buyers who skip ahead ("just send me a quote") are usually price-shopping; route them to a sized proposal only after confirming diagnosis and method.

## Premium-Rate Justification (four-pillar test)

A premium price requires at least three of: (1) measurable outcome the buyer cannot self-deliver, (2) accumulated proof in the buyer's category, (3) explicit risk transfer or guarantee, (4) named delivery method that limits buyer-side overhead. Two or fewer pillars means the price is exposed; either reduce the price or build the missing pillar before quoting.

## Discount Discipline (one rule)

No price reduction without a paired removal: cut scope, extend timeline, transfer a risk back to the buyer, or secure a multi-engagement commitment. A discount with no trade trains the buyer that the original price was theatre.
