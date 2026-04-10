# Security Skills Expansion — Design Spec

**Date:** 2026-04-10
**Author:** Brainstorm session with Peter Bamuhigire
**Status:** Approved for implementation (all 6 phases authorized sequentially)

---

## Goal

Close the security-related gaps identified in `docs/analysis/01-executive-summary.md` and `docs/analysis/04-gap-analysis.md` (GAP 10 in particular) by creating new skills and enhancing existing ones from a set of 14 EPUB source books.

## Gaps being closed

From executive summary:
- **Network security architecture** — firewall design, WAF, zero-trust, VPN patterns absent
- **Full secrets lifecycle** — Vault deep-dive, PKI, key rotation absent
- **Compliance-ready infrastructure** — ISO 27001, PCI-DSS controls absent (partial; full compliance deferred)

From GAP 10 ("Infrastructure & Platform Engineering Depth"):
- Network security section for `web-app-security-audit` → **expanded into a dedicated new skill**
- Linux hardening & performance tuning section for `cicd-jenkins-debian` → **expanded into a dedicated new skill**
- Additional web app depth, database security, iOS app security, and security automation

## Source material

14 EPUBs at `c:/Users/BIRDC/Downloads/`:

1. *Zero to Mastery in Network Security*
2. *Security Automation with Ansible 2*
3. *Mastering Linux Security and Hardening*
4. *Network Security Firewalls and VPNs* (Jones & Bartlett)
5. *Practical Linux Security Cookbook*
6. *The Web Application Hacker's Handbook* — Stuttard & Pinto (WAHH)
7. *Database and Application Security*
8. *Network Security Essentials: Applications and Standards* — Stallings (4th ed)
9. *iOS Application Security: The Definitive Guide for Hackers and Developers*
10. *Internet and Web Application Security*
11. *97 Things Every Application Security Professional Should Know*
12. *Grokking Web Application Security*
13. *Web Application Security*
14. `600604509.epub` — short PHP security primer (XSS, sessions, injection)

## Stack alignment

All skills target:
- Self-managed Debian/Ubuntu VPS (NSANO VPS-first model)
- Multi-tenant SaaS with PHP + Node.js + Android + iOS clients
- Open-source, self-hosted tooling; cloud services only as alternatives
- Practical, copy-pasteable configs over academic theory

## Scope boundaries

All files must adhere to `doc-standards.md`:
- ≤500 lines per markdown file (hard cap)
- Two-tier structure: `SKILL.md` as TOC/workflow entry point, `references/*.md` for deep dives
- Logical subdirectory grouping
- Proper frontmatter (name, description) on all `SKILL.md` files

---

## Phase 1 — `network-security` (NEW SKILL)

**Rationale:** Network security is genuinely absent. Three books provide enough content for a first-class skill rather than a section in another.

**Directory:** `c:/Users/BIRDC/.claude/skills/network-security/`

**Frontmatter description:**
> Use when designing, hardening, or auditing network-layer security for self-managed Debian/Ubuntu SaaS infrastructure — firewalls (nftables/UFW), WAF (ModSecurity + OWASP CRS), VPN (WireGuard, OpenVPN, IPsec), TLS/PKI ops, IDS/IPS (Suricata, Fail2ban), zero-trust, SSH hardening, DDoS mitigation, DNS security.

**SKILL.md outline (~400 lines):**
1. When to Use
2. Threat Model First
3. The 9 Network Security Domains (TOC)
4. Phase 1: Baseline Network Hardening Checklist (copy-paste Debian commands)
5. Phase 2: Service-Specific Hardening (Nginx, HAProxy, DB, Redis)
6. Phase 3: Zero-Trust Layer
7. Phase 4: Monitoring & Detection
8. Phase 5: Incident Response Runbook
9. Audit Checklist
10. Anti-patterns
11. References Index

**`references/` files (13):**

| File | Target lines | Primary source |
|---|---|---|
| `firewalls.md` | ~350 | Firewalls & VPNs (J&B), Zero to Mastery |
| `waf.md` | ~300 | Firewalls & VPNs, WAHH (attack patterns) |
| `tls-pki.md` | ~400 | Stallings ch. 17, Firewalls & VPNs |
| `vpn.md` | ~400 | Firewalls & VPNs, Stallings ch. 19 (IPsec) |
| `ssh-bastion.md` | ~250 | Firewalls & VPNs, Practical Linux Security |
| `ids-ips.md` | ~300 | Firewalls & VPNs IDS/IPS chapter |
| `ddos.md` | ~250 | Firewalls & VPNs, Zero to Mastery |
| `dns-security.md` | ~200 | Firewalls & VPNs, Stallings |
| `zero-trust.md` | ~300 | Zero to Mastery, Firewalls & VPNs |
| `crypto-fundamentals.md` | ~250 | Stallings (condensed reference) |
| `network-segmentation.md` | ~200 | Firewalls & VPNs, Zero to Mastery |
| `audit-checklist.md` | ~150 | Synthesis — 50-point yes/no audit |
| `incident-runbook.md` | ~200 | Synthesis — 5 common incidents |

**Cross-reference additions to existing skills:**
- `web-app-security-audit/SKILL.md` — add "Network Layer Security" section that points to `network-security`
- `cicd-jenkins-debian/SKILL.md` — add network hardening cross-reference
- `cicd-devsecops/SKILL.md` — add network defense cross-reference

---

## Phase 2 — `linux-security-hardening` (NEW SKILL)

**Rationale:** Two dedicated books (Mastering Linux Security & Hardening + Practical Linux Security Cookbook) on Linux hardening. GAP 10 recommends enhancing `cicd-jenkins-debian`, but the book content is deep enough to warrant a dedicated skill. `cicd-jenkins-debian` cross-references it.

**Directory:** `c:/Users/BIRDC/.claude/skills/linux-security-hardening/`

**Frontmatter description:**
> Use when hardening a Debian/Ubuntu server — user/group/permission audits, PAM/sudo hardening, SELinux/AppArmor MAC, auditd logging, kernel sysctls, file integrity (AIDE/Tripwire), PAM password policies, boot/grub security, rootkit detection (rkhunter/chkrootkit), automated patching, CIS benchmark compliance.

**SKILL.md outline (~450 lines):**
1. When to Use
2. Threat Model + Linux Attack Surface
3. The 10 Hardening Domains (TOC)
4. Baseline Hardening Checklist (fresh Debian 12 → hardened state)
5. Hardening Phases (user → perms → MAC → audit → kernel → monitoring)
6. Compliance Mapping (CIS, PCI-DSS-lite)
7. Audit Runbook
8. Anti-patterns
9. References Index

**`references/` files (11):**

| File | Target lines | Primary source |
|---|---|---|
| `users-groups-sudo.md` | ~300 | Mastering Linux Security ch. 3-4 |
| `file-permissions-acls.md` | ~300 | Practical Linux Security (perms chapters) |
| `pam-authentication.md` | ~250 | Mastering Linux Security PAM chapter |
| `selinux-apparmor.md` | ~400 | Mastering Linux Security MAC chapters |
| `auditd-logging.md` | ~300 | Practical Linux Security (auditd) |
| `kernel-sysctl-hardening.md` | ~300 | Mastering Linux Security kernel chapter |
| `file-integrity.md` | ~250 | Practical Linux Security (AIDE, Tripwire) |
| `rootkit-detection.md` | ~200 | Practical Linux Security (rkhunter, chkrootkit) |
| `patch-management.md` | ~200 | Mastering Linux Security (unattended-upgrades) |
| `boot-security.md` | ~200 | Mastering Linux Security (GRUB, UEFI) |
| `cis-benchmark-checklist.md` | ~300 | Synthesis — CIS Debian 12 controls |

**Cross-reference addition:**
- `cicd-jenkins-debian/SKILL.md` — add "Linux Hardening" section pointing to `linux-security-hardening`

---

## Phase 3 — Web App Security Depth (ENHANCEMENTS)

**Rationale:** Six books cover overlapping web app security territory. Rather than create new skills, enhance `web-app-security-audit`, `vibe-security-skill`, and `php-security` with new reference files that consolidate the depth.

**Files to create (added to existing `references/` directories):**

### `web-app-security-audit/references/` (NEW reference files)

| File | Target lines | Primary source |
|---|---|---|
| `wahh-attack-patterns.md` | ~450 | Web Application Hacker's Handbook — attack taxonomy |
| `auth-session-flaws.md` | ~400 | WAHH ch. 6-7; Web Application Security |
| `access-control-flaws.md` | ~350 | WAHH ch. 8; Internet & Web App Security |
| `input-validation-patterns.md` | ~350 | Grokking Web Application Security; WAHH |
| `business-logic-flaws.md` | ~300 | WAHH ch. 11; 97 Things |

### `vibe-security-skill/references/` (NEW reference files)

| File | Target lines | Primary source |
|---|---|---|
| `appsec-principles-97.md` | ~400 | 97 Things Every AppSec Pro Should Know |
| `grokking-fundamentals.md` | ~400 | Grokking Web Application Security (intro) |

### `php-security/references/` (NEW reference files)

| File | Target lines | Primary source |
|---|---|---|
| `xss-deep-dive.md` | ~250 | 600604509.epub + WAHH XSS chapter |
| `injection-attack-patterns.md` | ~300 | WAHH injection chapter + Grokking |

**SKILL.md updates:**
- `web-app-security-audit/SKILL.md` — update "See references/" pointer, add WAHH methodology brief
- `vibe-security-skill/SKILL.md` — add "See also: 97 Things principles, Grokking fundamentals"
- `php-security/SKILL.md` — add pointers to new deep-dive references

---

## Phase 4 — Database & Application Security (ENHANCEMENTS)

**Rationale:** One book covers database + app security. Enhance relevant existing skills rather than create new.

### Files to create

| File | Target lines | Skill |
|---|---|---|
| `mysql-best-practices/references/database-security-hardening.md` | ~400 | Database & Application Security |
| `postgresql-administration/references/postgres-security-hardening.md` | ~350 | Database & Application Security (Postgres-specific) |
| `php-security/references/db-layer-security.md` | ~250 | Database & Application Security (app-DB boundary) |

**SKILL.md updates:** Add reference pointers in affected skills.

---

## Phase 5 — `ios-app-security` (NEW SKILL)

**Rationale:** *iOS Application Security: The Definitive Guide for Hackers and Developers* is a deep book on iOS security. Existing `ios-development` and `ios-stability-solutions` cover general patterns but lack dedicated security depth. New skill complements them.

**Directory:** `c:/Users/BIRDC/.claude/skills/ios-app-security/`

**Frontmatter description:**
> Use when securing an iOS app — Keychain best practices, Secure Enclave, Data Protection classes, App Transport Security, cert pinning, jailbreak detection, runtime tamper detection, binary protection, reverse engineering defenses, code signing, privacy manifest, secure IPC.

**SKILL.md outline (~400 lines):**
1. When to Use
2. iOS Security Model Overview (sandbox, code signing, entitlements)
3. The 8 Security Domains (TOC)
4. Data-at-Rest Security
5. Data-in-Transit Security
6. Runtime Protection
7. Binary Protection
8. Privacy Compliance
9. Anti-patterns
10. References Index

**`references/` files (8):**

| File | Target lines | Primary source |
|---|---|---|
| `keychain-secure-enclave.md` | ~300 | iOS App Security (Keychain chapters) |
| `data-protection-classes.md` | ~250 | iOS App Security |
| `ats-cert-pinning.md` | ~300 | iOS App Security (network chapters) |
| `jailbreak-detection.md` | ~250 | iOS App Security |
| `runtime-tamper-detection.md` | ~300 | iOS App Security |
| `binary-protection.md` | ~250 | iOS App Security (anti-RE) |
| `code-signing-entitlements.md` | ~250 | iOS App Security |
| `privacy-manifest.md` | ~200 | Synthesis — iOS 17+ privacy manifest |

**Cross-reference addition:**
- `ios-development/SKILL.md` — add "Security" section pointing to `ios-app-security`

---

## Phase 6 — Security Automation (ENHANCEMENT)

**Rationale:** One book on Ansible security automation. Fits as an enhancement to `cicd-devsecops` rather than a standalone skill.

**Files to create:**

| File | Target lines | Source |
|---|---|---|
| `cicd-devsecops/references/ansible-security-automation.md` | ~450 | Security Automation with Ansible 2 |
| `cicd-devsecops/references/vault-secrets-lifecycle.md` | ~350 | Synthesis + Ansible book (Vault integration) |
| `cicd-devsecops/references/compliance-mapping.md` | ~300 | Synthesis — ISO 27001 + PCI-DSS mapping |

**SKILL.md updates:** Add new references to `cicd-devsecops/SKILL.md` TOC.

---

## Execution strategy

### Parallelization
Each phase produces largely independent files. Use the `Agent` tool (subagent_type=`general-purpose`) to delegate file-writing tasks in parallel batches. Each sub-agent receives:
- Target absolute file path
- Book path(s) and chapter guidance
- Exact outline / sections to cover
- Line budget and format rules (two-tier doc standards)
- Required frontmatter (for SKILL.md files)

### Phase execution order
Sequential by phase, parallel within each phase. Commit after each phase completes.

1. **Phase 1** — network-security (14 files) — split across 4 parallel agents
2. **Phase 2** — linux-security-hardening (12 files) — split across 3 parallel agents
3. **Phase 3** — Web app enhancements (9 files) — split across 3 parallel agents
4. **Phase 4** — DB security enhancements (3 files) — 1 agent
5. **Phase 5** — ios-app-security (9 files) — split across 2 parallel agents
6. **Phase 6** — cicd-devsecops enhancement (3 files) — 1 agent
7. **Repo index updates** — CLAUDE.md, README.md, PROJECT_BRIEF.md
8. **Final commit**

### Validation per phase
- `wc -l` on every created file, verify ≤500 lines
- Frontmatter YAML validity on SKILL.md files
- Cross-link check — all `references/X.md` references resolve
- Skill-safety-audit pass on new skills
- Commit with descriptive message

---

## Out of scope

- Compliance-ready infrastructure — full ISO 27001 / PCI-DSS control mapping (only a brief primer in `cicd-devsecops/references/compliance-mapping.md`)
- Kubernetes network policies (future `kubernetes-platform` skill per GAP 10)
- Cloud-specific network security (AWS Security Groups, GCP firewall rules) — mentioned only briefly
- Penetration testing methodology beyond what WAHH provides
- Wireless security, email security protocols, SNMP security — Tier 3 content explicitly dropped per user decision

---

## Success criteria

- 3 new skill directories created (`network-security`, `linux-security-hardening`, `ios-app-security`), each with valid `SKILL.md` and complete `references/` tree
- 14+ new reference files added to existing skills (web app, DB, cicd-devsecops)
- All files ≤500 lines
- `CLAUDE.md`, `README.md`, `PROJECT_BRIEF.md` repository indexes updated
- Clean git commits per phase
- All new skills cross-referenced appropriately from sibling skills
