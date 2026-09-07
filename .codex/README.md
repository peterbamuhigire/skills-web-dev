# Portable Codex model policy

This directory is a Codex adapter. It is deliberately shipped with each engine
so pulling an engine also brings its model policy and setup check. It contains
no domain skill and does not add to the active skill catalogue.

When Codex reads this engine's AGENTS.md, run the helper using an absolute path
resolved from that engine, even when the active project is elsewhere. Requires
Python 3.11+; resolve its executable path if `python` is not on PATH:

```text
python <engine-root>/.codex/ensure_model_policy.py --runtime codex --check
python <engine-root>/.codex/ensure_model_policy.py --runtime codex --apply
```

The first command checks local settings. Run the second only for reported drift;
Peter has authorised this bounded setup. The helper uses CODEX_HOME when set,
otherwise the current user's .codex directory. It preserves unrelated settings,
backs up touched files, and is idempotent. An unavailable Python/runtime or
unsafe merge is reported; do not replace a user's whole configuration manually.
No secrets or machine-specific configuration belong in this repository.

Claude must skip this setup and ignore the model pins. Shared skills, doctrine,
CLAUDE.md, permission settings and model choice for other runners remain intact.
Updating configuration does not change an already-running root model; start a
new Codex session when necessary and explicitly pin new execution spawns.

The compatibility implementation binds named roles through agents.<role>
config_file, tested against the local Codex 0.144.2 parser. That parser rejects
the newer default_subagent_model field; the default role and explicit spawn
instruction supply the execution default. Recheck supported configuration
syntax during every model-currentness review rather than guessing by version.

Concept reference: [donvito/codex-astra-luna-orchestrator](https://github.com/donvito/codex-astra-luna-orchestrator),
inspected at commit 21f4561656a1b8f2813828520357e3cd1785d50f on 2026-09-07.
The helper and policy here are independently implemented for these engines;
the upstream installer was not executed. See the engineering audit's
resume-2026-09-07/model-policy-sources.md for documentation and evidence limits.

A passing check verifies stored configuration and policy files. Profiles, project
configuration, session overrides and model entitlement can affect the effective
runtime; verify the active root and explicitly selected subagent models.

Existing custom role paths, extra role settings or differing user instructions
require explicit reconciliation: the helper stops before changing files. A
model-only policy update can be applied automatically when the role contract
still matches. Git pull delivers the adapter; Codex must read the engine router
and run the check to install it.
