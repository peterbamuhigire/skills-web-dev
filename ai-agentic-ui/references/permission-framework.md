# Tiered Permission Framework — Full Reference

Based on the Claude Code permission model. Three tiers, three required questions per prompt, explicit revocation scope.

---

## Tier Definitions

### Read-only

Tools that read state but never mutate.

- File reads, directory listings, grep/search.
- Web fetch (GET), RSS polls, public API GETs.
- Database SELECT against non-sensitive data.

**Default:** auto-execute, no prompt. Log to the Tier 3 audit record.

---

### Moderate

Tools with reversible or low-blast-radius side effects.

- Shell commands that do not touch the filesystem destructively.
- HTTP POST to sandboxed endpoints.
- Writes to scratch directories.

**Default:** prompt on first call in a session/directory. User may grant "don't ask again for this directory" or "for this session".

---

### Destructive

Tools with irreversible or high-blast-radius effects.

- File deletion, directory removal.
- Database INSERT/UPDATE/DELETE against production data.
- `rm -rf`, `git push --force`, `git reset --hard`.
- Sending external communication (email, SMS, webhook to third party).
- Financial transactions.

**Default:** prompt every single time. Never expose a "don't ask again" option for this tier.

---

## The Three Questions Every Permission Prompt Must Answer

### 1. What

The exact action, with parameters visible.

```
The agent wants to: DELETE 4 files
  - ./projects/old-draft.md
  - ./projects/old-draft.bak
  - ./projects/.tmp-123
  - ./projects/.tmp-124
```

Never say "the agent wants to clean up". Always show the concrete operation.

### 2. Why

One-sentence justification pulled from the plan.

```
Reason: Step 4 of plan - remove superseded drafts before final save.
```

If the reason is not obvious from the plan, the plan is too vague. Fix the plan, not the prompt.

### 3. How to revoke

Tell the user how to undo this approval later.

```
If you approve, this choice applies to this session only.
Revoke anytime: Settings -> Permissions -> Session grants.
```

---

## Sample Prompts

### Moderate tier (shell command)

```
Permission needed

What:   Run shell command: `npm install --save-dev vitest`
Why:    Step 2 of plan - install test runner before writing tests.
Scope:  This directory only, this session.
Revoke: Settings -> Permissions -> Per-directory grants.

[Approve once]  [Approve for session]  [Deny]
```

### Destructive tier (database write)

```
Permission needed - DESTRUCTIVE

What:   UPDATE 47 rows in `invoices` (set status='VOID')
Why:    Step 5 of plan - void invoices superseded by reissue.
Scope:  This single call. Will ask again next time.
Revoke: n/a - destructive calls are always confirmed.

[Approve]  [Show affected rows]  [Deny]
```

---

## Session vs Persistent Approval Rules

- **Per-call:** the default for destructive tools. Always.
- **Per-session:** resets when the session ends. Fine for moderate tools.
- **Per-directory:** persists across sessions for the same workspace. Appropriate for moderate tools where the user has established trust.
- **Global:** never offered for destructive tools. Only for explicitly read-only tool categories.

Revocation UI must be reachable in under 3 clicks from any screen.
