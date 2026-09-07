# Twelve-Engine Control Plane

The twelve local engines remain separate sources of truth. This control plane
provides the shared operating vocabulary for agents, commands, hooks, evidence,
handoffs, and bounded recovery. Its registry is
[`engine-control-plane.json`](engine-control-plane.json).

## Ownership

| Concern | Owner |
|---|---|
| Domain doctrine and specialist output | The routed domain engine |
| Agent topology and handoff protocol | `skills-web-dev` control plane |
| Source/currentness verification | `digital-research-skills` |
| Finance/accounting controls | `chwezi-accounting-doctrine` |
| Visual/presentation controls | `design-system-skills` |
| Windows host, domain, fleet, and hybrid administration | `windows-admin-engine-skills` |
| Political doctrine and political writing | `D:\political-skills` |
| Tool adapters and native hooks | Host adapter or CI; never duplicated in domain doctrine |

## Portfolio Kaizen currentness gate

Every Kaizen operation across all twelve engines—engine audits, skill or
reference edits, validator changes, routing changes, and standardisation
decisions—must begin with the Digital Research Engine's source-evaluation and
source-verification workflow. The canonical contract is
[`kaizen-currentness-gate.md`](../../digital-research-skills/docs/continuous-improvement/kaizen-currentness-gate.md).
Current standards, policies, laws, technologies, versions, commands, security
controls, benchmarks, and lifecycle claims require dated, scoped, reviewable
primary-source evidence. Missing or ambiguous evidence is `NOT_ASSESSED` and
blocks standardisation.

## Windows administration engine status

`windows-admin` is a first-class registry engine covering Windows workstations and
servers, Active Directory, identity/security, networking, storage, recovery, fleet,
and hybrid administration. Its canonical local checkout is
`C:\wamp64\www\windows-admin-engine-skills`; the registry contract is present, but
the checkout, `AGENTS.md`, and `docs/control-plane-adoption.md` are now present.
Its native catalogue, routing, source-ingestion, and control-plane checks pass;
live Windows/domain/fleet lab evidence remains claim-specific and must be marked
`NOT ASSESSED` when unavailable. Do not fabricate Windows procedures from Linux
or generic engineering guidance.

See [Windows administration engine status](engine-status/windows-admin-engine.md).

## Hook implementation policy

The registry describes the contract, not a claim that every host supports
native hooks. Implement each event using the strongest available adapter:

1. native lifecycle hook;
2. repository script or pre-commit check;
3. CI release gate;
4. explicit skill step with a recorded result.

Safety, evidence, destructive-action, and release hooks must fail closed or
return `NOT ASSESSED`. Advisory context and cost telemetry may fail open.

## Standard agent topology

`Router/Planner → Domain Worker → Evidence Collector → Adversarial Reviewer →
Gatekeeper/Release Captain`.

Use parallel workers only for independent evidence streams. One coordinator
owns the final synthesis and gate. The `Skill Librarian` may propose durable
improvements from repeated failures, but promotion requires a fixture, a
validation result, and an owner.

## Adoption matrix

Each engine registry entry identifies its domain agents, thin command surfaces,
minimum hooks, evidence types, and adoption document. The registry validator
checks all twelve engines and, when run with `--workspace-root C:\wamp64\www`,
verifies their routers and adoption documents are present:

```powershell
python scripts/validate_engine_control_plane.py --workspace-root C:\wamp64\www
```

This is intentionally a small control plane. It prevents duplicated persona
catalogues while making missing controls visible and testable.

### Repository checks and installed portfolio checks

With no `--workspace-root`, the validator checks the full registry's structure
and reports installed checkouts as NOT ASSESSED. This is the portable repository
gate declared in `.skills-engine/engine-manifest.yaml`; catalogue and routing
checks are separate declared gates.

With a workspace root, checkout checks are strict. `SKILL_ENGINE_ROOT_<ID>`
(hyphens replaced with underscores, uppercase) selects one authoritative
checkout. An invalid override fails rather than silently falling back. Without
an override, use the supplied workspace's engine directory. The research
directory is `digital-research-skills`. Home-directory duplicates are excluded.
Router and adoption files must resolve inside the selected checkout. Internal
links are accepted; external or broken contract links fail. An explicit
checkout override may itself be a link, with its resolved root as the boundary.

The user's 2026-09-06 scope contains eleven engines under `C:/wamp64/www`.
The registry additionally describes `political`, which is outside this local
operation. Repeated `--engine <id>` options limit installed-checkout validation
without omitting any registry-shape checks. Default installed validation still
checks every registry entry and fails on absent contracts.

Unit tests use temporary checkout fixtures, including missing contracts,
invalid overrides and path-traversal inputs. Set `SKILL_ENGINE_LIVE_TESTS=1`
to additionally check this host's confirmed eleven-engine installation.

## Human approval enforcement

Side-effecting tools must also use the versioned policy and executable gate in
[`approval-contract.md`](approval-contract.md), [`approval-policy.json`](approval-policy.json),
and [`../tools/approval_control_plane.py`](../tools/approval_control_plane.py).
Each domain adapter is validated by `scripts/validate_approval_adapters.py`.
The registry and skill text alone do not claim runtime enforcement: every host
path must route through the gate and pass the no-approval, stale-approval,
scope-change, self-approval, audit, kill-switch, idempotency, and verification
tests before it is marked enforced.
