# The Six Checkpoint Primitives

Every long-running agentic task needs all six. Missing any one breaks trust.

---

## 1. Checkpoint

A named, timestamped snapshot of state after each significant step. Git-like semantics.

**State shape:**

```
checkpoint_id:  cp_2026-04-25T14-02-11_step3
step:           3
label:          "After draft modification"
created_at:     2026-04-25 14:02:11 UTC
artifacts:      [draft-v2.md, decision-log.json]
parent:         cp_2026-04-25T14-01-48_step2
```

**UI:** every checkpoint appears as a node on the run timeline, clickable to inspect.

---

## 2. Rollback

One-click return to any earlier checkpoint. The action is destructive for work after the rollback point, so confirm first.

**State machine:**

```
[idle] --user clicks rollback--> [confirm-rollback]
[confirm-rollback] --user confirms--> [rolling-back]
                  --user cancels --> [idle]
[rolling-back] --success--> [restored]
               --failure--> [error-surface]
[restored] --auto--> [idle, at checkpoint N]
```

**Confirm copy:**

```
Roll back to checkpoint 3 "After draft modification"?
This will discard 2 later checkpoints and their work:
  - cp 4: "VAT field added"
  - cp 5: "Saved as v2"
```

---

## 3. Intermediate Output

Provisional outputs shown between steps. Two rules:

- Always labeled "Provisional — agent is still working".
- When the user edits intermediate output, the edit becomes input to the next step. The agent's original output is kept in the checkpoint, not overwritten.

**Layout:**

```
+----------------------------------------------+
|  Step 3 output (provisional)                 |
|                                              |
|  [ Editable text area with draft content ]   |
|                                              |
|  [Use this version]  [Keep agent version]    |
+----------------------------------------------+
```

---

## 4. Permission

Explicit user consent for side-effect actions. See `permission-framework.md`.

The permission primitive must be tied to the checkpoint stream: the permission prompt records which checkpoint it is gating, and approval/denial becomes part of the auditable record.

---

## 5. Edit/Error Surface

A single chronological panel showing:

- Agent errors (with full stack/trace in Tier 3).
- Retry attempts.
- User corrections.
- Permission denials.

**Layout:**

```
Run activity
  14:01:48  [OK]    Step 2 complete
  14:02:03  [RETRY] Step 3: tool returned 429, retrying (1/3)
  14:02:11 [EDIT]  User modified draft before step 4
  14:02:24 [DENY]  User denied destructive delete
  14:02:41 [ERROR] Step 5 aborted - no permission
```

Never split errors across multiple panels. One chronology, one source of truth.

---

## 6. Sources

Every factual claim or external input is attributed.

**Required fields:**

- Source name.
- Access time.
- Open-link (or "local file" with path).

**Inline format:**

```
The DPPA 2019 Act requires immediate breach notification to the PDPO
[source: ulii.org, accessed 2026-04-25 14:02, open].
```

Sources panel consolidates all citations used across the run, sortable by step.

---

## Interaction Between Primitives

```
         +------------+
         | Checkpoint |<------------------------+
         +------+-----+                         |
                |                               |
                v                               |
   +-----------------------+        +---------------------+
   | Intermediate output   |-edits->| (new step input)    |
   +-----------------------+        +---------------------+
                |
                v
       +--------+--------+
       | Permission gate |---denied---> [Edit/error surface]
       +--------+--------+
                |approved
                v
        (side-effect action)
                |
                v
         +------+-----+
         | Checkpoint |
         +------------+
```

Sources flow alongside the checkpoint stream; the Edit/error surface is a cross-cutting view over all of the above.
