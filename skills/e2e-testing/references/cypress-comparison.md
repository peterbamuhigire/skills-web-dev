# Playwright vs Cypress — Decision Aid

Use this table only when the team needs a justification record for tooling choice. The defaults in this repository are Playwright-first.

| Concern | Playwright | Cypress |
| --- | --- | --- |
| Browser coverage | Chromium, Firefox, WebKit (first-class) | Chromium-family + Firefox; WebKit experimental |
| Test process model | Out-of-process, Node-driven | Runs inside the browser |
| Multi-tab / multi-origin | First-class (`context.newPage`, cross-origin navigation) | Requires plugins / experimental flags |
| Mobile emulation | Native device descriptors (Pixel, iPhone, Mobile Safari UA) | Viewport-only |
| Component testing | Playwright Component Testing | Cypress Component Testing |
| Network mocking | `page.route` at the browser layer; `request` fixture for API-only | `cy.intercept` |
| Time-travel debugger | Trace Viewer (post-run) | Built-in command-log time travel (live, in-browser) |
| Parallelism | Workers + sharding free, no dashboard service required | Parallelism free; built-in record dashboard is paid |

## Pick Cypress when

- The team already uses Cypress and the cost of migration outweighs the gain.
- The app is a single-origin SPA and the time-travel debugger is the highest-value feature for the team.
- Investigations frequently stop at "what did the DOM look like at command N" — Cypress's live command log is faster than opening a trace.

## Pick Playwright otherwise

- Cross-browser parity matters (WebKit / Safari coverage).
- Tests cross origins, open new tabs, or drive native file dialogs.
- The runner needs to interleave UI flows with raw API calls (`request` fixture) without a plugin.
- CI sharding without a paid dashboard is a hard requirement.

## Migration notes

When converting a Cypress suite:

- `cy.get` → prefer `page.getByRole` / `getByLabel` over CSS selectors.
- `cy.intercept` → `page.route` with `route.fulfill` / `route.continue`.
- `cy.session` → `storageState` setup project.
- Custom commands → fixtures via `test.extend`.
- `cy.task` → run Node directly inside fixtures or in `globalSetup`.
