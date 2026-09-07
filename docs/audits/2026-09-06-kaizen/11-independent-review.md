# Independent review of validator changes

Review scope: the current working-tree changes to the control-plane validator,
quick validator, evidence contract gate, compliance scanner, engine manifest,
and changed or new tests. Implementation and skill evidence/metadata were not
edited. The local portfolio boundary and exclusion of the political checkout
follow the user's review brief. This is a code review, not a portfolio grade.

Verdict: address the discovery defect before accepting the empty-catalogue
guard. The path hardening also needs a containment decision and regression
coverage. These conclusions combine the changed code and the local probes
below (synthesis). No defect in an actual installed checkout is asserted.

## Findings

### Medium: discovery counts a directory named SKILL.md as a checked skill

The new recursive discovery yields every matching pathname without checking
that it is a file. A directory at `skills/family/ghost/SKILL.md` therefore
produces a skill candidate. The caller increments `matched` and `scanned`, but
the evidence checker returns no findings because the candidate's `SKILL.md`
is not a file. This bypasses the newly added empty-catalogue error, including
in strict mode. See [discovery and counters](../../../skills/sdlc-meta/skill-writing/scripts/contract_gate.py#L308),
the [early return](../../../skills/sdlc-meta/skill-writing/scripts/contract_gate.py#L118),
and [directory probe](#directory-probe) (synthesis).

The probe had no skill files, yet reported a scanned skill and successful
completion; the exact result is recorded in the [execution record](#directory-probe).
The previous discovery explicitly required a file; the new discovery loses
that check. The old gate also lacked the empty-catalogue error, so this is a
discovery regression and incomplete new guard, not a claim that empty scans
previously failed. Baseline comparison: `git show HEAD:skills/sdlc-meta/skill-writing/scripts/contract_gate.py`,
function `iter_skill_dirs`.

Recommended repair: require `skill_md.is_file()` before yielding its parent.
Add a directory-only fixture and assert discovery is empty, evidence checking
reports an error, and the CLI fails. Also exercise a valid skill beside such
a directory to ensure the directory does not inflate the scan result. These
are proposed acceptance checks (inference).

The new [real-catalogue test](../../../tests/test_contract_gate_discovery.py#L14)
repeats the same glob/filter expression without a file check, so its expected
set shares the defect. The [empty fixture](../../../tests/test_contract_gate_discovery.py#L30)
does not contain a directory named `SKILL.md` (synthesis).

### Medium: the new relative-path check does not establish checkout containment

`safe_relative_path` rejects lexical traversal and absolute paths, but
`resolve_engine_dir` accepts targets using `is_file()` without checking their
resolved location. A junction inside the selected checkout can therefore
supply both contract files from outside that checkout. See the
[path guard](../../../scripts/validate_engine_control_plane.py#L68),
[resolver](../../../scripts/validate_engine_control_plane.py#L59), and
[junction probe](#junction-probe) (synthesis).

In a disposable local fixture, `borrowed` was a junction to the real engineering
repository. The fixture registry used `borrowed/AGENTS.md` and
`borrowed/docs/engine-control-plane.md`. Both resolved outside the fixture
checkout, but validation returned no findings. This proves a containment gap
in the proposed hardening; it does not prove exploitation, unsafe writes, or
a compromised installed engine. The resolver's acceptance of linked files
predates this patch; the new lexical guard leaves that behaviour intact.
Evidence: [local junction result](#junction-probe).

If installed-checkout validation is intended to require locally contained
contracts, resolve the selected checkout and each contract target, reject
targets outside that checkout, and turn resolution failures into findings.
The boundary should be the selected checkout, including an explicitly
authorised override. If external contract links are intentionally supported,
make that exception explicit in the contract and output instead. These are
alternative remediation choices (inference).

Add an external directory-junction or symlink fixture, an internal link fixture,
and a broken-link fixture. Current [unsafe-path tests](../../../tests/test_engine_control_plane.py#L165)
exercise textual inputs without installed-checkout resolution; the
[installed fixtures](../../../tests/test_engine_control_plane.py#L113) create
ordinary files. Neither covers the demonstrated link boundary (synthesis).

## Checks and evidence boundary

The focused tests passed with the expected live-integration skips; see
[focused tests](#focused-tests). The user's statement that opt-in integration
tests passed is accepted as supplied context, not represented as reviewer
execution. No additional installed-portfolio run was performed.

No additional actionable regression was established in the changed description
validation, compatibility-list checks, adapter preservation, or manifest
commands. This is a bounded review result, not a correctness guarantee.
Evidence: scoped diff inspection, [compatibility tests](../../../tests/test_portable_compatibility.py),
and the [local checks](#other-local-checks) (synthesis).

The compliance inventory was run read-only across the active roots. Its
catalogue exceptions are not findings against this patch: skill evidence and
metadata belong to the other workers. The scanner's unconditional successful
exit is pre-existing and was not treated as a new regression.

Currentness preflight: `NO_TIME_SENSITIVE_CLAIMS` about external products,
standards, laws, versions, or platform support. Sources are the working-tree
code, its Git baseline, and reviewer-run local probes. Their freshness is
context-bound to this review session; support is limited to the inspected
snapshot and observed host behaviour. Re-review after implementation changes.
External currentness, Linux/macOS execution, production behaviour, and a
full security audit are `NOT_ASSESSED`. The optional portfolio craft guide
was unavailable at the repository-specified path; no source found there.

## Reviewer execution record

These are primary local observations from this review. Synthetic fixture names
below identify test setup, not real skills or installed portfolio members.
Registry edits were in memory only. No implementation file was changed.
The temporary junction and empty fixture directories were removed after the
probes; the junction target was preserved.

### Focused tests

Command, run from the engineering repository:

```powershell
python -m pytest -q tests/test_engine_control_plane.py tests/test_contract_gate_discovery.py tests/test_portable_compatibility.py tests/test_all_engine_currentness_policy.py
```

Observed terminal output, reproduced verbatim:

```text
40 passed, 3 skipped in 0.77s
```

### Directory probe

Setup: create only the directory `catalogue/skills/family/ghost/SKILL.md`
inside a disposable temporary lab. Import the current `contract_gate.py`,
set its `REPO_ROOT` to that fixture catalogue, inspect discovery, call
`run_evidence_check(None)`, then call `main()` with
`sys.argv = ['contract_gate.py', '--evidence', '--strict']`.

Observed terminal output, reproduced verbatim:

```text
actual_skill_files= []
discovered= ['skills/family/ghost']
evidence_result= ([], 1, 0)
contract-gate: evidence: scanned 1 | 0 errors | 0 warnings | 0 exempt
cli_exit= 0
```

### Junction probe

Setup: create a disposable `skills-web-dev` fixture directory and a `borrowed`
junction targeting `C:/wamp64/www/skills-web-dev`. Load the real registry into
memory and replace only the engineering entry's router and adoption paths
with the `borrowed` paths described in the finding. Patch registry reading
to return that JSON and set `SKILL_ENGINE_ROOT_SKILLS_WEB_DEV` within the
probe process to the fixture checkout. Call
`validate_registry(lab, {'skills-web-dev'})`. Other registry entries remain
subject to structural validation, without installed-checkout checks.

Observed terminal output, reproduced verbatim:

```text
router lexically_safe= True resolved_outside_checkout= True
adoption_doc lexically_safe= True resolved_outside_checkout= True
registry_findings= []
```

### Other local checks

| Executed command | Observed result and limit |
| --- | --- |
| `python scripts/validate_engine_control_plane.py` | Passed registry validation; installed checkout scope explicitly unassessed. |
| `python -X utf8 scripts/skill_catalog_guardrails.py --report-only` | No findings reported, including the source-ingestion checks. Report-only exit status was not used as proof. |
| `python -X utf8 scripts/routing_smoke_test.py` | No failures reported. |
| `python tests/agent-integration/test_skills_web_dev_agent_contract.py` | Local agent contract passed; universal catalogue unavailable and explicitly unassessed. |
| `python -X utf8 skills/sdlc-meta/skill-engine-audit/scripts/engine_compliance.py --root . --active-root skills --active-root 00-meta-initialization` | Inventory completed without safe fixes; metadata/content exceptions reserved for their owners. |

## Snapshot and handoff

Baseline identifier observed with `git rev-parse HEAD`:
`8058c4535716a97638faed7c885930335538d5ad`.
The findings refer to uncommitted changes over that baseline.

File hashes observed with `Get-FileHash` for the finding-bearing snapshot:

```text
scripts/validate_engine_control_plane.py
E0D7046FCE89939F69A0A143C23549594D965BE28D8372F02541C15621D8E350
skills/sdlc-meta/skill-writing/scripts/contract_gate.py
C61D2D15023EABE865AAC02F39D076EB04BA6DA64BDFE53A01D51AE1BC24A789
```

Implementation owner handoff: repair file-only discovery; decide and enforce
the contract-link boundary; add the listed failure fixtures; rerun the focused
tests and probes. Reviewer sign-off on those repairs remains `NOT_ASSESSED`.

Report anti-slop check: findings identify the trigger, affected code,
reproduction, consequence, and acceptance evidence; inherited behaviour is
distinguished from regression. No unsupported score or general readiness
claim is assigned. This is the reviewer's qualitative document check.

## Fix recheck disposition

Disposition: the discovery finding and contract-containment finding are
closed for the rechecked snapshot. This disposition supersedes the pending
repair sign-off above; the original findings, hashes, and negative execution
evidence remain unchanged. Scope was limited to these repairs and their
regression tests. No broader review or implementation edit was performed.

- Discovery now requires a file before yielding a skill directory. The
  directory-only regression exercises the error result and strict CLI failure;
  its mixed fixture discovers only the real skill. Evidence:
  [updated discovery](../../../skills/sdlc-meta/skill-writing/scripts/contract_gate.py#L308),
  [regression fixture](../../../tests/test_contract_gate_discovery.py#L37), and
  [recheck execution](#recheck-execution) (synthesis).
- The resolver strictly resolves the selected checkout and each contract
  target, requires containment and a file, and returns failure on resolution
  exceptions. The link fixtures accepted internal targets, rejected external
  targets, and rejected broken targets during the reviewer-run tests. Evidence:
  [updated resolver](../../../scripts/validate_engine_control_plane.py#L59),
  [link fixtures](../../../tests/test_engine_control_plane.py#L199), and
  [recheck execution](#recheck-execution) (synthesis).

Independent supplementary probes confirmed rejection when only the router or
only the adoption document pointed outside the checkout. Injected
`PermissionError` and `RuntimeError` exceptions also returned failure. These
exception probes establish handler behaviour, not real permission-denied or
filesystem-loop execution. POSIX symlink execution remains `NOT_ASSESSED`;
the local test run exercised the Windows junction branch. Evidence: the
[link helper](../../../tests/test_engine_control_plane.py#L174) and the primary
execution record below (synthesis).

No remaining defect was established in the requested fixes. The user's
full-suite pass report is supplied context; only the focused execution below
is claimed as independently rerun.

### Recheck execution

Executed from the repository, setting the live-check flag only in the child
Python process:

```python
import os, pytest
os.environ['SKILL_ENGINE_LIVE_TESTS'] = '1'
raise SystemExit(pytest.main([
    '-q', 'tests/test_contract_gate_discovery.py',
    'tests/test_engine_control_plane.py',
]))
```

Observed terminal output, reproduced verbatim:

```text
31 passed in 0.95s
```

Supplementary probe setup: import the current validator and patch
`engine_candidates` to return the real engineering checkout. For exception
checks, patch `Path.resolve` to raise the indicated exception and assert the
resolver returns `None`. For boundary checks, leave resolution real and use
`../digital-research-skills/SKILL.md` for each contract field in turn, with
`AGENTS.md` as the other field. Both files already existed; the probes made
no filesystem changes.

Observed terminal output, reproduced verbatim:

```text
permission_resolution_error_rejected=True (injected exception)
loop_resolution_error_rejected=True (injected exception)
outside_target_rejected=True adoption_doc
outside_target_rejected=True router
```

Rechecked file hashes observed with `Get-FileHash`:

```text
scripts/validate_engine_control_plane.py
45092AA0A1936FEC284681B2160B877926141166CFE5A4A579799F5C155B9B78
skills/sdlc-meta/skill-writing/scripts/contract_gate.py
6995EB1A36083C4B1CA7F400E3BC6539B0505BBE1EE18CFFE01483E556809BDB
tests/test_contract_gate_discovery.py
C84E475BCA9CF1A7A2389CF2714CDC35FE9B9DF5D59C46FD19414E6BC39AB7AA
tests/test_engine_control_plane.py
89717D41CD3ABB4368393307552E267391308F8A070F42E0B999E717C1B16EBC
```
