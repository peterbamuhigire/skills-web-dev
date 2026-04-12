# Review And Release

## Pull Request Checklist

- [ ] The diff is scoped to one coherent change.
- [ ] Commit history is readable enough for later diagnosis.
- [ ] Tests cover the changed behavior at the right level.
- [ ] Migration, config, or dependency changes are called out explicitly.
- [ ] Risky areas and rollback notes are documented when relevant.

## Reviewer Checklist

- [ ] Does this introduce a behavioral regression?
- [ ] Are auth, tenancy, concurrency, and error paths handled correctly?
- [ ] Is the migration safe for live data?
- [ ] Are tests missing where failures are plausible?
- [ ] Is the change understandable for future maintainers?

## Release Checklist

- [ ] Main branch is green and deployable.
- [ ] Release notes reflect user-visible and operator-visible changes.
- [ ] Rollback path is known.
- [ ] Post-deploy verification steps are defined.
- [ ] Monitoring exists for the highest-risk change in the release.
