# Memory Tiers — Schemas and Lifecycle

## Short-Term (Turn Buffer)

Holds the most recent N exchanges in the active conversation. Used for: pronoun resolution, immediate context.

**Storage:** Redis hash or DB row tagged `ephemeral`.

**Schema:**
```redis
HSET memory:short:{conversation_id}
  user_msg_n      "How do I..."
  assistant_msg_n "You can..."
  user_msg_n+1    ...
EXPIRE memory:short:{conversation_id} 86400
```

Or DB:
```sql
CREATE TABLE agent_memory_short (
  id              BIGINT PRIMARY KEY,
  conversation_id BIGINT NOT NULL,
  tenant_id       BIGINT NOT NULL,
  user_id         BIGINT NOT NULL,
  turn_index      INT NOT NULL,
  role            ENUM('user','assistant','tool','system') NOT NULL,
  content         TEXT NOT NULL,
  tokens          INT,
  created_at      DATETIME NOT NULL,
  INDEX (conversation_id, turn_index)
);
```

Sliding window: keep last K turns (default 20) by `turn_index DESC`. Older turns evict.

Cost note: short-term sits in the prompt every turn. Long buffers explode token cost. Compress aggressively (`summarise older turns into a paragraph; keep last 6 raw`).

## Working (Episode Memory)

Holds the current agent task's intermediate state — plan, observations, retries.

**Storage:** DB rows tied to `agent_tasks.id`.

**Schema:**
```sql
CREATE TABLE agent_memory_working (
  id          BIGINT PRIMARY KEY,
  task_id     BIGINT NOT NULL,
  tenant_id   BIGINT NOT NULL,
  user_id     BIGINT,
  kind        ENUM('plan','observation','intermediate','correction','retry_context') NOT NULL,
  content     JSON NOT NULL,
  step_index  INT,
  created_at  DATETIME NOT NULL,
  INDEX (task_id, kind, step_index)
);
```

Lifecycle:
- Created during task execution.
- Retained for 7 days after task completes (for support investigations, replay).
- Auto-purged after 7 days unless flagged for compliance hold.

Working memory is **not** searched by the agent. It's loaded by task_id when the loop resumes (after HITL or crash).

## Long-Term (Semantic Memory)

Cross-conversation, per-tenant durable facts.

**Storage:** vector store + DB row (canonical text + metadata).

**Schema:**
```sql
CREATE TABLE agent_memory_long (
  id              BIGINT PRIMARY KEY,
  tenant_id       BIGINT NOT NULL,
  subject_user_id BIGINT,                   -- user this fact is about (often the actor; may be a customer)
  written_by_user_id BIGINT,                -- user during whose session this was written
  scope           ENUM('global','conversation','task') NOT NULL DEFAULT 'task',
  kind            ENUM('preference','entity_attribute','workflow_shortcut','correction','consent') NOT NULL,
  subject         VARCHAR(256),             -- e.g., "customer:ACME" or "user:42"
  fact            TEXT NOT NULL,            -- canonical natural-language fact
  structured      JSON,                     -- structured representation if applicable
  source          ENUM('user_stated','inferred','derived','admin_set') NOT NULL,
  confidence      FLOAT NOT NULL,
  consented_at    DATETIME,
  expires_at      DATETIME,
  created_at      DATETIME NOT NULL,
  embedding_id    VARCHAR(64) NOT NULL,
  INDEX (tenant_id, scope, kind),
  INDEX (subject_user_id),
  INDEX (subject)
);
```

Vector store entry:
```
{
  "id":          "{embedding_id}",
  "vector":      [...],
  "metadata": {
    "tenant_id":         42,
    "memory_id":         12345,
    "subject_user_id":   17,
    "subject":           "customer:ACME",
    "kind":              "entity_attribute",
    "scope":             "global"
  }
}
```

## Querying

```python
def recall(query: str, ctx: ToolContext, scope: str = None, k: int = 5):
    emb = embed(query)
    filt = {"tenant_id": ctx.tenant_id}
    if scope == "global":
        filt["scope"] = "global"
    elif scope == "conversation":
        filt["$or"] = [{"scope": "global"}, {"conversation_id": ctx.conversation_id}]
    elif scope == "task":
        filt["$or"] = [{"scope": "global"}, {"task_id": ctx.task_id}]
    results = vstore.query(vector=emb, filter=filt, top_k=k)
    enriched = []
    for r in results:
        row = db.get(agent_memory_long, r.metadata["memory_id"])
        if row and (row.expires_at is None or row.expires_at > now()):
            enriched.append({
                "fact": row.fact,
                "confidence": row.confidence,
                "source": row.source,
                "age_days": (now() - row.created_at).days,
            })
    return enriched
```

## Writing

```python
def write_long(fact: str, kind: str, subject: str, source: str, confidence: float, ctx: ToolContext):
    if confidence < 0.8 and source != "user_stated":
        raise LowConfidence()
    if contains_pii(fact, categories=PII_DO_NOT_STORE):
        raise NonStorablePII()
    if not user_consented_to_memory(ctx):
        raise NoConsent()
    emb_id = vstore.insert(embed(fact), metadata={
        "tenant_id": ctx.tenant_id,
        "subject_user_id": ctx.user_id,
        "subject": subject,
        "kind": kind,
        "scope": "task",  # default narrow
    })
    db.insert(agent_memory_long, {
        "tenant_id": ctx.tenant_id, "fact": fact, "kind": kind,
        "subject": subject, "subject_user_id": ctx.user_id,
        "source": source, "confidence": confidence,
        "consented_at": now(), "embedding_id": emb_id,
        "expires_at": now() + DEFAULT_RETENTION,
    })
```

## Promotion / Demotion

Users can promote a memory from `task` → `conversation` → `global` scope (a "remember this everywhere" action), and demote (`global` → `conversation`). All transitions audited.

## "What I Remember About You" Surface

```
Memories for user@example.com               [Search]   [Export]   [Delete all]

PREFERENCE
  • Prefers concise answers                  [ Edit ] [ Forget ]
  • SI units                                  [ Edit ] [ Forget ]

CUSTOMER FACTS (ACME)
  • Billing contact: ben@acme.example         [ Edit ] [ Forget ]
  • Preferred currency: USD                   [ Edit ] [ Forget ]
  • Net-30 payment terms                      [ Edit ] [ Forget ]

WORKFLOW SHORTCUTS
  • Monthly close: reports in order A,B,C     [ Edit ] [ Forget ]

[ Show inferred low-confidence (3) ]
```

Hidden low-confidence row: lets the user confirm/correct/forget inferences before they harden.

## Audit Log

Every long-term memory write writes one row to `agent_memory_audit`:

```sql
CREATE TABLE agent_memory_audit (
  id              BIGINT PRIMARY KEY,
  memory_id       BIGINT,
  operation       ENUM('create','update','promote','demote','forget','expire','erasure_cascade') NOT NULL,
  by_actor        VARCHAR(64),       -- user_id, agent_task_id, or system
  reason          TEXT,
  before          JSON,
  after           JSON,
  created_at      DATETIME NOT NULL
);
```

Audit rows are immutable. The forget operation deletes the memory but the audit row remains (with PII redacted as needed).
