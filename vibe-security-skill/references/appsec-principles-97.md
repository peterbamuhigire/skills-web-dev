# AppSec Principles — Distilled from 97 Things Every Application Security Professional Should Know

Collective wisdom from 60+ AppSec practitioners, distilled into actionable principles for engineers and security champions.
Reach for this when making architectural or process decisions about AppSec, not when fixing a single bug.

## How to use this reference

This is a principle catalogue, not a checklist. Each item is a 2-4 line rule with a short "why" and sometimes a "how". Read a theme before starting any cross-cutting activity (threat model, tool rollout, incident review). For concrete technical defences in code, pair this with `grokking-fundamentals.md` and the existing OWASP mappings.

Nine themes:

1. Security culture and shift-left
2. Threat modelling and adversarial thinking
3. SDLC integration and secure paved roads
4. Testing and verification (SAST / DAST / IAST / pen test / bug bounty)
5. Vulnerability management and triage
6. Incident response and post-breach learning
7. People, training and security champions
8. Metrics that actually drive outcomes
9. Software supply chain and operations

## 1. Security culture and shift-left

- **Security is a business enabler, not a blocker.** Frame every control as protecting revenue, trust, or time-to-market. Why: teams that see security as an obstacle will route around it.
- **Shift left AND shift right.** Design-time threat modelling catches architectural flaws; runtime monitoring catches what only production can reveal. Why: either alone leaves large gaps.
- **Security in the Definition of Done.** No story is "done" until the security acceptance criteria are met and evidence is attached. Why: it stops the "we'll add security later" tax.
- **Make the secure path the easy path.** Build paved roads (pre-approved libraries, templates, CI scans) so the default is safe. Why: developers pick the option with least friction.
- **Earn trust before demanding changes.** Security programmes run on goodwill; fix your own tooling noise before lecturing engineers. Why: credibility is the real currency of AppSec.
- **Security owns outcomes, not gates.** Measure fewer incidents and faster patch cycles, not approvals issued. Why: gates create theatre; outcomes build a real programme.
- **Treat security debt like technical debt.** Track it, prioritise it, burn it down in planned sprints. Why: invisible debt compounds until a breach forces attention.
- **Communicate risk in business language.** Dollars, downtime, and regulatory impact beat CVSS scores for leadership. Why: funding follows comprehension.
- **Reward reporting, never punish it.** Developers who raise a flag must feel celebrated, not shamed. Why: psychological safety is the cheapest control you can buy.
- **Security is everyone's job, but not everyone's expertise.** Embed experts in teams; don't expect every engineer to become a specialist. Why: the wrong expectation leads to shallow knowledge everywhere.

## 2. Threat modelling and adversarial thinking

- **Four questions frame every threat model.** What are we building? What can go wrong? What are we going to do about it? Did we do a good job? Why: the Shostack frame keeps sessions focused and actionable.
- **Threat model before code freeze, not after.** A threat model done during design can still change the architecture cheaply. Why: threat-modelling a shipped system mostly documents regret.
- **Use STRIDE as a vocabulary, not a straitjacket.** Spoofing, Tampering, Repudiation, Information disclosure, DoS, Elevation of privilege covers 90% of realistic threats. Why: a shared vocabulary makes threats comparable across teams.
- **Threat models are living documents.** Revisit them whenever the trust boundaries, data flows, or auth model change. Why: stale models mislead; a missing sticky note is better than a wrong diagram.
- **Draw the data-flow diagram first.** Before listing threats, draw the boxes and arrows. Why: you cannot threat-model a system you cannot picture.
- **Identify assets and entry points explicitly.** Name the crown-jewel data, then map every path that touches it. Why: without an asset list, teams threat-model trivia and ignore the important things.
- **Assume the attacker is already inside.** Threat-model lateral movement, not just perimeter breach. Why: zero-trust design is only real if you model post-breach behaviour.
- **Involve developers in the threat model.** Engineers who built the system spot 80% of the flaws once prompted. Why: security-led models miss implementation reality.
- **Record mitigations AND accepted risks.** An unmitigated threat is not a failure; an unacknowledged one is. Why: explicit acceptance gives you a paper trail and future review item.
- **Threat-model the build and deploy pipeline, not just the app.** CI/CD is an attacker's dream target. Why: SolarWinds and Codecov taught us this the expensive way.

## 3. SDLC integration and secure paved roads

- **Security requirements are functional requirements.** Write them as user stories with acceptance criteria. Why: what is not in the backlog does not get built.
- **Code review must include a security lens.** At minimum, check input trust, auth, and secret handling on every PR. Why: review is the cheapest mitigation you will ever deploy.
- **Pre-commit hooks catch low-hanging fruit.** Secret scanners, linters, and format checks fail fast and locally. Why: saving a developer a CI round-trip is also saving budget.
- **Dependency management is a first-class concern.** Pin versions, track licences, and automate upgrade PRs. Why: every dependency is a supply chain attack waiting to happen.
- **Golden images and base containers, maintained by security.** Every team starts from a hardened, patched base. Why: common baselines let you patch a vuln once, not a thousand times.
- **Infrastructure as code must pass the same gates as application code.** Terraform and Helm charts are code; scan them for misconfigurations. Why: most cloud breaches start with misconfigured IAM or buckets.
- **Secure-by-default frameworks beat secure-by-discipline.** Choose a framework whose default config is safe. Why: discipline decays; defaults persist.
- **Use CODEOWNERS and provenance signals.** Require security review on sensitive paths (auth, crypto, payments). Why: the right eyes on the right files at the right time.
- **Document the security decisions in ADRs.** Future engineers need to know why a control exists before they remove it. Why: tribal knowledge leaves with the engineer who had it.
- **Treat the SDLC as an attack surface.** The pipeline, artefact store, and deploy keys all need their own controls. Why: compromising one merge button beats compromising the whole fleet.

## 4. Testing and verification

- **SAST is best for early, broad coverage — with tuning.** Static analysis finds classes of flaws (injection, insecure APIs) across the whole repo cheaply. Why: but untuned SAST drowns teams in false positives and loses trust fast.
- **DAST finds what runs, not what was written.** Dynamic scans test the live app and catch runtime-only issues (session, auth, misconfig). Why: SAST cannot see a broken access control on a real endpoint.
- **IAST blends static and dynamic context at runtime.** Agents instrument the running app and see real data flow. Why: fewer false positives, but only on exercised code paths.
- **Fuzzing is underused and underrated.** Feeding random or mutated inputs finds crashes, parsing bugs, and logic flaws cheaply. Why: OSS-Fuzz alone has found thousands of real CVEs.
- **Manual pen testing still matters.** Humans find business-logic flaws that no scanner understands. Why: "transfer negative money" will never show up in a rule file.
- **Bug bounty is not a substitute for an AppSec programme.** Bounties find issues your programme missed; they do not replace the programme. Why: running one without process leads to burnout and hostile researchers.
- **Start bug bounty private, go public slowly.** Invite a handful of researchers, tune your triage, then open up. Why: a public launch without triage capacity creates chaos.
- **Test coverage ≠ security coverage.** High line coverage can still miss every auth check. Why: you need dedicated security test cases, not just unit tests.
- **Red team exercises validate detection, not just prevention.** If the red team gets in and you never saw them, your logging is broken. Why: defenders learn more from being hit than from passing an audit.
- **Every bug found in production must become a test.** Regression tests in CI stop the exact same flaw returning. Why: without this, you are paying for the same lesson twice.

## 5. Vulnerability management and triage

- **CVSS is an input, not a decision.** Exploitability, exposure, and business impact matter more than the raw score. Why: a CVSS 9.8 on an internal-only admin tool is not your top priority.
- **Use EPSS to prioritise what attackers actually exploit.** The Exploit Prediction Scoring System models real-world exploitation likelihood. Why: focusing on "exploited in the wild" beats chasing every high CVSS.
- **Patch velocity is a leading indicator.** Measure mean time from CVE disclosure to production deploy, per severity band. Why: velocity tells you whether the pipeline and culture are working.
- **Patch SLAs must match the risk, not the calendar.** Critical external, seven days; internal lows, 90. Why: arbitrary SLAs lose legitimacy on both sides.
- **Build an explicit risk-acceptance process.** Unpatchable vulns need a documented owner, mitigation, and review date. Why: informal acceptance becomes permanent ignorance.
- **Fix classes, not instances.** If you found an XSS in a template helper, audit every call site of that helper. Why: attackers look for patterns; so should defenders.
- **Triage everything; fix what matters.** Every incoming finding gets reviewed; not every finding gets a ticket. Why: auto-creating tickets without triage kills backlogs.
- **Track the age of open findings, not just count.** A 200-day-old critical is more dangerous than a 5-day-old one. Why: aged vulns reveal process bottlenecks, not just engineering capacity.
- **Close the loop with the developer, not just the ticket.** Explain the fix, the test, and the why. Why: teaching the team makes the next bug cheaper to fix.
- **Deduplicate scanner output ruthlessly.** One underlying flaw should create one ticket, not 40. Why: phantom backlogs destroy morale and hide real work.

## 6. Incident response and post-breach learning

- **Have a written runbook, practised quarterly.** Muscle memory during an incident beats improvisation every time. Why: nobody reads a document for the first time at 3 a.m.
- **Detect, contain, eradicate, recover, learn.** The five-phase IR loop is still the backbone of every good response. Why: skipping a phase (usually "learn") is what creates repeat incidents.
- **Preserve evidence before you clean up.** Snapshot the machine, dump memory, export logs. Why: law enforcement and post-mortem both need artefacts you only get once.
- **Communicate early, often, and in plain language.** Internal stakeholders and affected customers deserve accurate updates. Why: silence in an incident fuels rumours worse than the incident.
- **Have an out-of-band channel ready.** If your regular comms are compromised, you need Signal, a phone bridge, or a printed call tree. Why: email may be the thing you cannot trust.
- **A blameless post-mortem is non-negotiable.** Focus on systems and defaults, not individuals. Why: blame-free culture produces more honest data.
- **Invite engineering, not just security, to the post-mortem.** The people who built the system see fixes security never would. Why: shared ownership accelerates prevention.
- **Follow up on action items with deadlines.** A post-mortem without tracked actions is a group therapy session. Why: without deadlines, lessons never become changes.
- **Credential stuffing is a long tail.** Once a password list leaks, attacks can continue for years. Why: detection fatigue makes this worse; you need sustained monitoring.
- **Practise the ransomware scenario specifically.** Assume the domain controller and backups are both compromised. Why: ransomware is the highest-likelihood, highest-impact scenario for most orgs.

## 7. People, training and security champions

- **Security champions live in product teams, not security teams.** Engineers who love security get time allocated and a direct line to the AppSec team. Why: federation scales; central gatekeeping does not.
- **Train the just-in-time, not the just-in-case.** Targeted training after a relevant finding beats annual e-learning. Why: humans retain what they just used.
- **Teach the why, not just the what.** Engineers who understand why SQL injection works write safer queries everywhere. Why: understanding generalises; checklists do not.
- **Empathy is a technical skill.** AppSec professionals work with people under pressure; tone changes outcomes. Why: a hostile finding gets closed wontfix; a kind one gets fixed and learned from.
- **Make learning resources frictionless.** Internal wikis, short videos, pair reviews — meet people where they are. Why: a 400-page PDF is a memorial, not a training.
- **Security champions need visible career value.** Reward the role with promotion, pay, and recognition. Why: unpaid extra work eventually dies from burnout.
- **Role-specific training beats one-size-fits-all.** Backend, frontend, mobile, and SRE each see different threat classes. Why: generic training feels irrelevant and gets tuned out.
- **Run regular tabletop exercises.** Simulated incidents teach judgment under pressure. Why: tabletops surface gaps no runbook can predict.
- **Rotate security engineers through product teams.** Embedded stints build trust and spread knowledge. Why: empathy and context flow both ways.
- **Celebrate the saves.** Publish "we found and fixed X before it shipped" stories internally. Why: positive case studies recruit future champions.

## 8. Metrics that drive outcomes

- **Measure outcomes, not activity.** Vulns found is vanity; time-to-remediate and escape rate are real. Why: activity metrics reward busywork.
- **Escape rate: bugs found in production vs earlier stages.** This measures whether shift-left is working. Why: if escape rate is rising, your tests are slipping.
- **Mean time to detect (MTTD) and respond (MTTR).** The two numbers that define how fast you can contain an incident. Why: breaches get expensive in hours, not days.
- **Percentage of services with a threat model.** Coverage is a leading indicator of maturity. Why: but the threat model must be real, not a ticked box.
- **False-positive rate on security tooling.** Above 20% and developers will tune you out. Why: noisy tools train teams to ignore alerts.
- **Patch SLA compliance by severity.** Are you actually meeting your promised windows? Why: tracking shows whether SLAs are feasible or aspirational.
- **Dependency freshness.** Median age of dependencies in production. Why: stale deps are a proxy for supply chain risk.
- **Production secret scan findings.** If secrets keep ending up in source control, training is failing. Why: it measures the gap between policy and practice.
- **DORA metrics correlate with security.** Elite performers (lead time under an hour, deployment multiple times a day) also have lower change failure rates. Why: velocity and safety are the same flywheel.
- **Avoid vanity dashboards.** If a metric has never triggered a decision, stop reporting it. Why: every number you track costs attention.

## 9. Supply chain and operations

- **Every dependency is a trust decision.** Review the project, its maintainers, its signing, and its release cadence. Why: you are importing the supply chain of everyone upstream.
- **Produce an SBOM for every release.** Software Bill of Materials tells you what is in a build, which is table stakes after Log4Shell. Why: during an incident, "which products include X?" must be answerable in minutes.
- **Consume SBOMs from suppliers.** Demand them; correlate them with your CVE feeds. Why: SBOMs are only useful if you actually look at them.
- **Pin, verify, and reproduce builds.** Use lockfiles, hash-pin, and reproducible builds where possible. Why: without pinning, your "tested" build is not the one that shipped.
- **Isolate build infrastructure.** CI runners should have only the secrets they need and should be ephemeral. Why: long-lived runners accumulate blast radius.
- **Sign your artefacts.** Sigstore, Cosign, or equivalent; verify signatures at deploy time. Why: unsigned artefacts can be swapped in the registry.
- **SLSA levels are a reasonable maturity target.** Supply chain Levels for Software Artefacts gives a progression to aim for. Why: not perfect, but better than no roadmap.
- **Secrets go in a vault, not in environment variables checked into git.** Rotate automatically; audit access. Why: leaked secrets still dominate breach causes.
- **Runtime protection (WAF, RASP) is a seatbelt, not a brake.** It buys you time to patch, it does not replace patching. Why: teams that lean on a WAF stop fixing code, which is a strategic mistake.
- **Observe what you defend.** Logs, metrics, traces — without them you are deploying blind. Why: you cannot respond to what you cannot see.

## The top 10 non-obvious principles

Ten ideas from the book that reliably surprise engineers new to AppSec.

1. **Fewer, higher-quality findings beat exhaustive ones.** A scanner that finds 3 real issues beats one that finds 300 and is 70% noise.
2. **The security team is a force multiplier, not a blocker.** Their value comes from what others ship safely, not what they ship themselves.
3. **Secrets management is a people problem as much as a tools problem.** No vault survives a culture that copy-pastes.
4. **A WAF rule that nobody understands is a future outage.** Document every custom rule.
5. **Pen test reports are a snapshot, not a posture.** Monthly scans and continuous monitoring tell you more than an annual test.
6. **Training that is not measured is not training.** Track behaviour change, not attendance.
7. **Least privilege is aspirational without regular review.** Permissions accumulate; you must prune them.
8. **Log everything security-relevant, but beware of logging sensitive data.** Design audit logs carefully — they themselves become crown jewels.
9. **Most breaches are boring.** Misconfigured buckets, old creds, unpatched libraries. Focus there before exotic zero-days.
10. **The best AppSec engineers teach more than they scan.** Their output is developer capability, not tickets closed.

## Anti-patterns (what the book warns against)

- Security gates that approve or reject without feedback. Tell engineers what to fix and how, or do not block.
- Shipping a scanner without training, tuning, or ownership. Tools without a programme create noise and cynicism.
- Metrics that measure activity instead of outcomes. "Vulnerabilities detected" rewards adding more scanners, not fixing more bugs.
- Treating compliance as the target. Compliance is a floor, not a ceiling.
- The "security says no" reflex. A good AppSec team offers a secure path, not a veto.
- Running a bug bounty without internal triage capacity. Researchers will leave and reputation will suffer.
- Dumping raw scanner output into developer tickets. Triage, deduplicate, and contextualise first.
- Annual training as the only training. Once-a-year videos do not change behaviour.
- Ignoring third-party code review. Dependencies are your code; treat them that way.
- Security decisions made in secret. Transparent decisions survive leadership changes.
- Over-reliance on perimeter defences. Zero-trust assumes the perimeter has already failed.
- Storing secrets in environment variables only. They leak via logs, crash dumps, and container images.
- Skipping post-mortems on "small" incidents. Small today, big tomorrow.
- Building custom crypto. Use audited libraries, always.
- Letting pen-test findings age. If nothing changes after a pen test, the pen test was wasted budget.

## Cross-references

- `grokking-fundamentals.md` — the developer-facing fundamentals that back up these principles.
- `owasp-mapping.md` — OWASP Top 10 mapping used by this skill.
- `authentication-security.md` — auth-specific guidance referenced in Section 2.
- `access-control.md` — authorisation and least-privilege patterns.
- `server-side-security.md` — runtime, headers, and config hardening.
- `client-side-security.md` — CSP, CSRF, and output encoding in the browser.
- `file-upload-security.md` — a common high-risk entry point.
- Skills: `web-app-security-audit`, `code-safety-scanner`, `cicd-devsecops`, `network-security`, `linux-security-hardening`, `llm-security`, `ai-security`.
