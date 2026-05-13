# UI Lint Checks

Mechanical checks. Run as part of CI for any UI repo that consumes the finance design tokens.

## Grep / AST patterns

| # | Pattern (regex / AST query) | What it catches | Severity |
|---|---|---|---|
| L-01 | `<button[^>]*>\s*(Delete|Remove)\b` on posted records | Destructive verbs on posted records | blocker |
| L-02 | `text-(green|red)-` or `bg-(green|red)-` in JSX outside `<StatusChip>` and `<MoneyCell signed>` | Non-semantic colour use | blocker |
| L-03 | `<td[^>]*class="[^"]*"[^>]*>\s*\$?\d` without `tabular-nums` ancestor | Money cell without tabular numerals | major |
| L-04 | `<Card[^>]*>[^<]*\d` in a dashboard tile without `to=` / `onClick` | Summary tile without drilldown | major |
| L-05 | `status\s*=\s*['"](active|pending|done|cancelled)['"]` on finance records | Free-text status outside controlled taxonomy | blocker |
| L-06 | Any `.css` / `.scss` / `.module.css` for a finance report page that lacks `@media print` | Missing print stylesheet | major |
| L-07 | `gross.*total` rendered as a single column where a tax code exists on the source | Gross-only display conflating net / tax / gross | blocker |
| L-08 | `<input type="search">` on amount columns with `step="any"` | Amount field accepts non-numeric | major |
| L-09 | `<form>` without `aria-labelledby` on posting forms | Accessibility | major |
| L-10 | `confirm("…")` for posting confirmations | Native confirm instead of designed confirmation summary | major |
| L-11 | `JSON.stringify` of money values without `toFixed` / decimal control | Floating-point money rounding risk | blocker |
| L-12 | `setTimeout` motion on posted-money rendering | Motion on posted numbers | blocker |
| L-13 | Token literal hex outside the token bundle | Hard-coded colour | major |
| L-14 | `:hover` actions without keyboard equivalent | Mouse-only interaction | major |
| L-15 | `display: none` for print-only content without `@media print` reveal | Print content hidden | major |

## React-specific AST checks

```js
// rule: no destructive verbs on posted records
{
  "selector": "JSXElement[openingElement.name.name='Button'][openingElement.attributes.value.value='Delete']",
  "deny-when-parent-prop": "status in ['posted', 'reversed', 'matched']"
}
```

```js
// rule: every Card displaying a money summary must drill down
{
  "selector": "JSXElement[openingElement.name.name='Card']:has(MoneyCell)",
  "require-prop-on-self": "to | onClick"
}
```

```js
// rule: status strings must match the taxonomy
{
  "selector": "Literal[parent.property.name='status']",
  "value-must-be-in": [
    "draft","awaiting-approval","posted","reversed",
    "matched","unmatched","exception","locked","released",
    "requested","approved","rejected","partial-match",
    "pending-evidence","submitted","acknowledged","filed",
    "efris-submitted","efris-confirmed","efris-rejected","efris-cancelled",
    "etims-submitted","etims-confirmed","etims-rejected",
    "open","soft-closed","reopened","archived",
    "mapped","tie-out-ok","tie-out-fail","suspense","sign-off",
    "received","counted","adjusted","written-off"
  ]
}
```

## CSS checks

```css
/* All money cells must have tabular numerals. */
.money { font-variant-numeric: tabular-nums; }
.money:not([class*="font-variant-numeric"]) {
  /* lint failure */
}
```

## Visual-regression checks

- Snapshot every component story.
- Snapshot every print stylesheet (using `puppeteer` or `playwright` print emulation).
- Snapshot RTL layouts when RTL is enabled per locale.
- Snapshot dark mode where enabled.

## Manual review checks

Items the lint cannot catch — require human review:

- Microcopy tone (workflow vs ledger surface vocabulary).
- Whether a drilldown actually leads to source evidence.
- Whether status colour pairs with text consistently across the page.
- Whether the print rendering is auditor-legible.
- Whether period state is reflected accurately in the chrome.

## CI integration

```yaml
# example GitHub Actions step
- name: Finance UI lint
  run: npm run lint:finance-ui
- name: Print snapshot
  run: npm run snapshot:print
- name: Visual regression
  run: npm run vr:finance
```

`npm run lint:finance-ui` invokes the rules above plus the project's standard linter.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
