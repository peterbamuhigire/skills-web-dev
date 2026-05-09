---
name: no-json-in-ui
description: Hard rule for end-user-facing forms — operators must never be required
  to type, paste, or read JSON, YAML, XML, or any other machine-serialised payload.
  Always wrap structured data behind buttons, dialogs, repeaters, toggles, dropdowns,
  multi-selects, or chip pickers. Convert to JSON in the background only. Applies
  to web (Bootstrap 5/Tabler + SweetAlert2), Android (Jetpack Compose), iOS (SwiftUI).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# No JSON in the UI
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- A form needs to capture structured data (lists of objects, key/value maps, enums-with-attributes, capability flag sets, JSON columns).
- The current implementation uses a `<textarea>`, `<input>`, code editor, `contenteditable`, or any field that asks the user to read or type JSON / YAML / XML / a serialised blob.
- Designing CRUD pages over JSON-typed database columns (`*_json`, `JSONB`, `JSON`).
- Reviewing an existing screen that violates the rule.

## Do Not Use When

- A developer-only tool intended for in-house engineering staff (debug consoles, raw query workbenches, hidden super-admin overrides explicitly labelled "developer / not for end users") — even then, prefer a structured editor and offer a "raw" toggle as a last resort.
- The JSON IS the deliverable (export buttons, download links, API doc snippets, copy-to-clipboard helpers). These display JSON, they don't ask the user to type it.

## Required Inputs

- The shape of the structured data you need to capture (schema, enum values, nesting depth).
- The runtime context (web / Android / iOS / hybrid) and which UI library is in use.
- The persistence target (DB column type, API field, on-disk file).
- Whether the user is end-user-facing (clinician, cashier, owner, patient) or platform-developer.

## The Rule

> **An end user MUST NEVER be required to enter JSON, YAML, XML, or any other machine-serialised payload to use the application. Always provide a structured UI — buttons, popups, repeaters, toggles, dropdowns, multi-selects, chip pickers — and convert to/from the serialised form invisibly in the background.**

This is non-negotiable for any production user surface. Treat it the same as "never expose database error stack traces to the user" or "never log raw passwords." A textarea labelled `Capabilities JSON` is a UX bug and a failure of professional craft.

### Why

1. **Accessibility & literacy.** Field clinicians, cashiers, receptionists, and patients are not developers. Asking them to type `{"ipd": false, "lab": true}` is asking them to do work the software should do for them.
2. **Data quality.** Hand-typed JSON yields trailing commas, unquoted keys, smart quotes from copy/paste, mismatched braces, the wrong enum spelling. The system silently accepts garbage.
3. **Discoverability.** The set of allowed keys / values is invisible. The user has to read source code or guess.
4. **Internationalisation.** A JSON editor cannot show translated key labels — the operator sees raw English machine identifiers in a French / Swahili UI.
5. **Mobile.** JSON typing is hostile on touch keyboards. It violates the touch-target and form-UX rules from `form-ux-design`.
6. **Audit & undo.** Structured forms can validate per-field, highlight changes, and produce diffs. JSON blobs cannot.

## Workflow

1. **Identify every JSON-shaped field on the screen.** Look for:
   - `<textarea name="*_json">`, `<input name="*_json">`
   - `name=` ending in `_payload`, `_config`, `_options`, `_metadata`, `_settings`, `_capabilities`, `_codes`, `_tags`, `_meta`
   - Any field with `placeholder='[{...}]'` or `placeholder='{"...":"..."}'`
   - DB columns of type `JSON`, `JSONB`, `LONGTEXT` containing structured data, `MEDIUMTEXT` likewise.
   - Front-end code that calls `JSON.stringify(formField.value)` directly on user input.

2. **Decide the right widget for each shape:**

   | Data shape | Web (Bootstrap 5/Tabler) | Android | iOS |
   |---|---|---|---|
   | Map of fixed boolean flags (e.g. `{"opd":true,"lab":false}`) | row of `.form-switch` toggles, one per known key, with translated labels | `Switch` row in `Column` | `Toggle` in `Form` |
   | Closed enum picker (one of N) | `<select>` with translated options, or radio cards | `DropdownMenu` / segmented control | `Picker` |
   | Multi-select from a closed list | chip multi-select / `.form-check` checklist | `FilterChip` row | toggleable `Chip`s |
   | List of objects (vendors, drawers, line items) | repeater: list of cards + "Add" button → SweetAlert2 popup with the item's fields → render row with Edit + Remove | `LazyColumn` of cards + FAB → bottom sheet form | `List` + sheet form |
   | Free-form key/value pairs that the user genuinely defines | repeater of `{key, value}` rows with a typeahead on `key` against a known schema where possible | same | same |
   | Date / time / duration encoded in JSON | native picker (`flatpickr` on web, `DatePicker` on mobile) — never a typed string | `DatePicker` | `DatePicker` |
   | Nested or arbitrary tree (rare) | step-by-step wizard or scoped editor; only as last resort use a JSON view *with* a structured editor toggle, default to structured | wizard | wizard |

3. **Make the conversion invisible:**
   - Server keeps the JSON column unchanged. The UI converts.
   - On read: server-rendered hidden `<input type="hidden" data-json-shape="...">` carrying `JSON.stringify(value)`. Page-load JS hydrates the visible widget from this hidden value.
   - On write: when any structured widget changes, recompute and write back the JSON to the hidden input, then `dispatchEvent(new Event('change', {bubbles:true}))` so the surrounding form / autosave layer picks it up.
   - The hidden input is the single source of truth on submit; the form posts JSON exactly as before.

4. **Preserve translations:** every visible label, placeholder, dropdown option, validation message goes through the project's `__()` helper (or platform equivalent). The internal JSON keys (`opd`, `ipd`, …) stay machine-stable.

5. **Validate at the widget, not at JSON-parse time.** Required toggles, mutually-exclusive options, ranges, max-list-length, etc. are enforced in the dialog before the JSON is computed. The submitted JSON is therefore always well-formed and within schema.

## Quality Standards

- Zero textareas / inputs whose visible label or placeholder mentions JSON, YAML, the bracket characters `[]{}`, or the word "format".
- Every dropdown-of-strings backed by a closed enum **must** present translated option labels, not the raw enum codes.
- Every list-of-objects **must** support Add, Edit, and Remove, with a confirmation step on Remove.
- The structured widget **must** round-trip cleanly: render existing data, edit, save, reload, render again — no drift.
- Accessibility: every widget must be keyboard-operable, have associated labels, and announce validation errors to screen readers (`aria-invalid`, `aria-describedby`, role="alert" on toasts).
- No "advanced / raw JSON" toggle on end-user pages. If the structured form cannot express what's needed, the schema is wrong; redesign the schema.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| `<textarea>` labelled "Capabilities JSON" | User must type valid JSON; collision with translated UI; mobile-hostile | Row of toggles per known capability key |
| Adding `placeholder='[{"name":"...", "currency":"UGX"}]'` | Reveals the schema as decoration but still requires the user to type JSON | "Add cash drawer" button → popup with `{name, currency}` fields |
| Auto-uppercasing or auto-quoting tricks on a JSON textarea | A heuristic patch over the wrong UI | Replace the textarea entirely |
| "JSON validator" tooltip below a JSON textarea | Doubles down on the wrong abstraction | Replace with a structured form |
| Code editor (Ace / CodeMirror / Monaco) for end-user data | A nicer JSON editor is still a JSON editor | Same — replace with structured form |
| Client-side check `JSON.parse(value)` and surfacing parse errors | Punishing the user for the form's failure to model the data | Move the field set to a structured widget |
| YAML / TOML / XML in a textarea | Same problem; same fix | Same |
| Asking the user to enter a bare ISO 8601 date string in a text input | A serialised data format rendered as text | Native date picker |

## Outputs

- A revised page or form where every structured-data field is captured through a typed widget appropriate to its shape.
- A short note on the JSON schema preserved on the wire (so backwards compatibility is obvious).
- For non-trivial repeaters, a small JS helper file that owns the read / render / write / dispatch cycle, listening to the platform's hydration event so initial values populate after async draft loads.

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| UX | Before / after of the page | Screenshots or markdown described UI | "Replaced JSON textarea with 8 toggles" |
| Implementation | The structured widget + the hidden JSON conversion | Source files | `step-06-cash-bank.js`, `step-15-vendors-insurers.js` |
| Verification | The wire payload still validates server-side | One smoke-test request | `curl … | jq` |

## References

- See `form-ux-design` for the underlying input-anatomy rules these widgets must satisfy.
- See `practical-ui-design` for spacing, hierarchy, and visual rhythm of the resulting forms.
- See `webapp-gui-design` for Tabler conventions around modals, switches, and chip lists.
- See `healthcare-ui-design` when the structured data carries clinical safety implications (e.g. capability flags that gate workflows).
- See `vibe-security-skill` for input-validation patterns when the structured payload reaches a database column.

<!-- dual-compat-end -->

## Decision Tree

```
Is this end-user-facing?
├── No (engineering-only tool)
│   └── Prefer structured form anyway. If JSON unavoidable, label it "Developer-only" and require an explicit toggle.
└── Yes
    └── Does the field hold structured data?
        ├── No → ordinary input/select/etc. — no special action.
        └── Yes
            ├── Is the schema closed (known set of keys / enum values)? → use a typed widget per the table above.
            ├── Is the schema open key/value? → repeater of {key,value} rows; never a JSON textarea.
            └── Is the data deeply nested with arbitrary structure? → step-by-step wizard. If genuinely impossible, the data model is wrong; refactor the schema before the UI.
```

## Quick Audit Snippet

Run this against any web app to find candidate violations:

```bash
grep -rEn '<textarea[^>]*name="[^"]*_json"' --include='*.php' --include='*.html' --include='*.tsx' --include='*.jsx' src/ public/
grep -rEn 'placeholder="\[\{|placeholder="\{' --include='*.php' --include='*.html' src/ public/
grep -rEn '__e?\([^)]*JSON' --include='*.php' src/ public/
```

Each hit is a page to redesign. None should remain in production.

## Real-World Example (from Medic8)

Before: onboarding step 6 had two `<textarea>`s asking the operator to type `[{"name":"Reception Drawer","currency":"UGX"}]`. The placeholder was the schema. The format hint mentioned JSON. Save errors were silent because the JSON parser tolerated mistakes the schema did not.

After: two card lists with "Add cash drawer" / "Add bank account" buttons. SweetAlert2 popup with native fields (name, currency dropdown defaulting to facility currency). Edit and Remove on each row. The hidden `data-field="cash_drawers"` input still carries the same JSON wire format — the wizard's autosave layer changed nothing. Translation keys for every label, in three locales.

The same pattern was applied to vendors, insurers, and the mobile-money "Custom providers" extension. The diff to the wire payload was zero. The diff to user experience was the difference between a tool people use and a tool people abandon.
