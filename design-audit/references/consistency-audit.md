# Consistency Audit

Use this reference when the main question is whether the interface feels coherent and
predictable rather than merely attractive.

## Audit lens

Check whether similar things look and behave similarly:

- headings
- buttons
- cards
- forms
- tables
- status states
- dialogs
- destructive actions
- token usage
- component documentation vs shipped UI

## What to flag

- Multiple button hierarchies for the same level of importance
- Same concept named differently across screens
- Inputs that change label placement or error style between flows
- One-off gradients, shadows, radii, or padding values
- Controls that require hover to reveal clickability
- Duplicate components that solve the same problem with small visual differences
- Documentation or design files that no longer match the implemented component
- Raw values in product code where system tokens should exist

## Severity rule

Raise severity when inconsistency increases user hesitation, causes mistakes, or breaks
learned behavior across key flows.

Raise severity further when inconsistency also increases maintenance cost or reveals that the source of truth has drifted.
