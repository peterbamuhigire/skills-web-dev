# Interface Consistency

Use this reference when building SaaS screens that must feel coherent across modules.

## Screen contract

Every new screen should answer these the same way as the rest of the product:

- Where am I?
- What is primary on this screen?
- What is clickable?
- What state is this data in?
- What happens next?

## Reusable rules

1. Keep one dominant action per view.
2. Use the same component for the same interaction class.
3. Empty, loading, error, and success states should share structure and tone.
4. Tables, forms, filters, and dialogs should preserve alignment and spacing logic across modules.
5. Avoid introducing a new visual pattern until the existing primitives clearly fail.

## Fragile areas

- Inline actions mixed with row clicks
- Filters that change location or shape between screens
- Destructive actions that move between dropdown, button, and dialog styles
- Pages with different heading scales for the same hierarchy level
