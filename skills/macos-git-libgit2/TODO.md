# TODO: macos-git-libgit2 Skill

## Purpose

Create a skill for building macOS Git clients using libgit2, SwiftGit2, and actor-isolated local Git operations.

## Why GlassHub Needs It

- GlassHub depends on full offline Git operations.
- Correct staging, merge, rebase, cherry-pick, stash, and diff workflows require deep Git behavior knowledge.
- libgit2 object lifetimes and threading rules need careful handling.

## Study Before Writing

- Pro Git internals.
- libgit2 API docs.
- SwiftGit2 source and examples.
- Git index, object database, refs, reflog, packfiles, and merge machinery.

## Skill Should Cover

- Git actor boundary and repository handle lifecycle.
- Status, log, diff, branch, commit, merge, rebase, stash, and remote operation patterns.
- Credential helper, HTTPS, SSH, and GitHub token interactions.
- Fixture repository design for tests.
- Conflict detection and recovery UI requirements.
- Performance strategies for large histories and large diffs.

## Starter Evidence To Collect

- Fixture repositories with known histories and conflicts.
- Mapping table from libgit2 errors to app-domain errors.
- Checklist for safe history-rewriting operations.
