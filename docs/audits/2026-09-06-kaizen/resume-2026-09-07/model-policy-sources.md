# Codex model policy: evidence and portability

Peter requested this topology on 2026-09-07: Astra for the root and reviewer,
Luna pinned for execution. He then required engine-carried setup across
computers and explicitly preserved Claude's full functionality. This is a user
decision, not a measured claim that the topology is optimal for every task.

## Source register

All sources below were accessed 2026-09-07; review at the next Kaizen start,
no later than 2026-09-13 for this implementation. Owner: Peter; verifier: Codex.

| ID | Primary source and locator | Scope/date | Support and uncertainty |
|---|---|---|---|
| MODEL-ASTRA | [OpenAI Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra) | Current model ID; publication date not established; snapshot 2026-09-07 | Supports model identity. Workload advantage in these engines is NOT ASSESSED. |
| MODEL-LUNA | [OpenAI Luna model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna) | Current model ID; publication date not established; snapshot 2026-09-07 | Supports identity and the provider's cost-sensitive positioning, not measured local savings. |
| MODEL-CURRENT | [Official model catalogue](https://developers.openai.com/api/docs/models/all) and [latest-model guidance](https://developers.openai.com/api/docs/guides/latest-model) | Opened 2026-09-07; undated page snapshots | Current provider guidance includes Astra and Luna. No replacement to Peter's explicit selection is justified by this source check alone. |
| CODEX-ROLES | [Official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents), Choosing models and Custom agents | Current documentation snapshot 2026-09-07 | Describes defaults and role overrides. New scalar defaults are incompatible with the installed CLI; local parsing controls this implementation. |
| CODEX-REVIEW | [Official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), review_model | Current documentation snapshot 2026-09-07 | Supports a separate review model. A file update does not establish the model of an existing thread. |
| CONCEPT | [donvito repository](https://github.com/donvito/codex-astra-luna-orchestrator), config, role files, orchestration skill, installer | Commit 21f4561656a1b8f2813828520357e3cd1785d50f, fetched 2026-09-07 | First-party evidence of the concept only; not authority for Codex compatibility. Installer read, not executed. |

Freshness: time-sensitive/context-bound to these snapshots. Confidence: high
for the model names and inspected configuration contract; measured comparative
quality, latency, cost savings and cross-computer execution are NOT ASSESSED.
No new model-performance numbers are admitted.

## Observed compatibility

The local CLI reports 0.144.2. It rejected the documented newer
`agents.default_subagent_model` scalar as an invalid AgentRoleToml value.
The replacement uses `agents.<role>.config_file` bindings and explicitly
model-pinned role files; `codex features list` then exited zero and
`codex doctor --json` reported `config.load=ok` with root `gpt-6-astra`.
Doctor also reports unrelated environment conditions; this is not an overall
doctor pass.

Both the bundled and refreshed CLI catalogue output listed Luna but omitted
Astra. The active collaboration tool offers both, and an actual Luna handoff
worker was spawned. CLI Astra inference and future-computer model entitlement
are NOT ASSESSED. Do not replace the user's requested Astra ID because a
separate catalogue omitted it. Check actual runtime availability at use time.

## Adaptation and decision

Retain the requested pins. The concept's bounded execution and separate review
fit the user decision. This implementation adds per-engine distribution,
idempotent local checking, backups, safe merge checks, and an explicit
Claude exclusion. It does not install the third-party skill, alter domain
catalogues, change permissions, or execute its installer.

Named execution roles include default, worker, explorer, tester and researcher;
the reviewer is Astra. The agent instruction also requires an explicit model
on every execution spawn, including bounded/no-history forks where needed.
This supplies a default under the older parser without adding unsupported
keys. It is not an administrator lock against user overrides.

Future Kaizen MUST check new model releases and actual runtime availability,
compare suitable roles using relevant evidence, and record a retain/change
decision. A new release alone does not silently replace Peter's pins.

The temporary personal setup was a compatibility probe; durable ownership is
the adapter shipped with each engine. The setup helper is the repeatable way
to bring those settings to a new machine. Pulling Git alone cannot hot-switch
an already-running model or bypass Codex's trust boundary.
