# Codex adapter acceptance ? 2026-09-07

GPT-5.6 Luna implemented the helper; GPT-6 Astra independently reviewed it.
Temporary-home probes verified rejection of unsafe backup paths, preservation
of existing role restrictions and custom bindings, model-only drift repair,
rollback after injected write failures, and a Claude no-op with populated home.
Initial overwrite and backup-path findings were repaired before distribution.

Root inspected and explicitly adopted the four personal role files created
by this task's earlier compatibility probe, with a separate local backup.
This adoption does not authorise replacing unknown custom roles on other machines.
A relative-path compatibility finding during local installation was referred
back for a focused repair and regression.

Acceptance concerns stored policy and bounded filesystem behavior. Effective
runtime overrides, entitlement, cross-computer execution and POSIX permission
behavior are not certified by these Windows tests. Domain readiness scores
remain NOT ASSESSED.

Final local installation found and repaired equivalent-relative-path rejection
and blank-line growth around managed tables. Regression checks cover both.
Root verified actual local apply/check success and unchanged bytes and mtimes
on repeat apply; each of the eleven adapters independently passes the same
local check. No personal config values outside the owned keys changed.

Astra independently accepted the final table-boundary fix using 18 temporary
fixtures and four repeat apply/check cycles per fixture. Role-table ordering,
whitespace and relative paths preserved managed and backup bytes/mtimes and
unrelated project, feature and custom-agent settings. No blocking findings remain.
