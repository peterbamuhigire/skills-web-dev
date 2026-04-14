# Phase 01: Infrastructure Foundation

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the cloud deployment and CI/CD skills that allow every product built with this engine to reach production.

**Architecture:** Two new skill directories (`cloud-architecture`, `cicd-pipelines`) plus targeted enhancements to `cicd-devsecops`. All new skills must follow the dual-compatible portable execution contract so they run equally under Claude Code and Codex.

**Tech Stack:** AWS/GCP, Docker, Docker Compose, GitHub Actions, HashiCorp Vault, Fastlane, OWASP Dependency-Check, Trivy.

---

## Dual-Compatibility Contract (apply to every new skill in this phase)

Every `SKILL.md` created here must contain all sections in this order:

```
Use When → Do Not Use When → Required Inputs →
Workflow → Quality Standards → Anti-Patterns → Outputs → References
```

Required frontmatter metadata block:

```yaml
metadata:
  portable: true
  compatible_with: [claude-code, codex]
```

Optional Claude Code helpers go in a **Platform Notes** section — never in a `Required Plugins` blocker that would prevent Codex execution.

Validate every skill after writing:
```bash
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

---

## Task 1: Create `cloud-architecture` skill

**Files:**
- Create: `cloud-architecture/SKILL.md`
- Create: `cloud-architecture/references/aws-core-services.md`
- Create: `cloud-architecture/references/docker-compose-patterns.md`
- Create: `cloud-architecture/references/deployment-patterns.md`

**Step 1:** Write `cloud-architecture/SKILL.md` covering:
- Docker: Dockerfile best practices, multi-stage builds, .dockerignore, layer caching
- Docker Compose: local dev stack, service dependencies, volume mounts, env files
- AWS core: EC2 (instance types, AMIs, user-data), S3 (static hosting, presigned URLs, lifecycle), RDS (managed MySQL/PostgreSQL, automated backups, read replicas), IAM (least-privilege roles, instance profiles)
- Deployment patterns: blue-green, canary, rolling — when to use each
- SSL/TLS: Certbot + Let's Encrypt on Nginx
- CDN: CloudFront / Cloudflare for static assets
- Auto-scaling: EC2 Auto Scaling Groups, target tracking, warm pools
- Cost optimisation: Reserved Instances, Spot for non-critical, S3 Intelligent-Tiering

Anti-Patterns must include: credentials in Dockerfiles, single-AZ production, root IAM for apps, fat runtime containers.

**Step 2:** Write `references/aws-core-services.md` — service-by-service CLI reference.

**Step 3:** Write `references/docker-compose-patterns.md` — full local stack template (Node.js + MySQL + Redis + vector DB sidecar).

**Step 4:** Write `references/deployment-patterns.md` — blue-green and canary runbooks with rollback steps.

**Step 5:** Validate.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py cloud-architecture
```
Expected: PASS, no line-count violations.

**Step 6:** Commit.
```bash
git add cloud-architecture/
git commit -m "feat: add cloud-architecture skill (AWS, Docker, deployment patterns)"
```

---

## Task 2: Create `cicd-pipelines` skill

**Files:**
- Create: `cicd-pipelines/SKILL.md`
- Create: `cicd-pipelines/references/github-actions-workflows.md`
- Create: `cicd-pipelines/references/ios-fastlane-pipeline.md`
- Create: `cicd-pipelines/references/android-pipeline.md`

**Step 1:** Write `cicd-pipelines/SKILL.md` covering:
- GitHub Actions: workflow syntax, triggers, jobs, steps, matrix builds, reusable workflows
- Secrets: `${{ secrets.X }}`, environment-level secrets, OIDC for AWS (no static keys)
- Node.js pipeline: install → lint → test → build → Docker build → push ECR → deploy
- PHP pipeline: composer install → PHPStan → PHPUnit → deploy via SSH/rsync
- Environment promotion: dev → staging → production gates with manual approval steps
- Caching: `actions/cache` for node_modules, Gradle, CocoaPods, pip
- Rollback: automatic rollback on health-check failure, manual rollback trigger

**Step 2:** Write `references/github-actions-workflows.md` — copy-paste YAML templates for Node.js, PHP, and Docker.

**Step 3:** Write `references/ios-fastlane-pipeline.md` — lanes for test, beta (TestFlight), release; GitHub Actions + Match code signing.

**Step 4:** Write `references/android-pipeline.md` — Gradle build, unit tests, signed AAB, Google Play via Fastlane Supply.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py cicd-pipelines
git add cicd-pipelines/
git commit -m "feat: add cicd-pipelines skill (GitHub Actions, Fastlane, environment gates)"
```

---

## Task 3: Enhance `cicd-devsecops`

**Files:**
- Modify: `cicd-devsecops/SKILL.md` (add three sections, stay ≤ 500 lines)
- Create: `cicd-devsecops/references/vault-operations.md`
- Create: `cicd-devsecops/references/compliance-controls.md`
- Create: `cicd-devsecops/references/container-runtime-security.md`

**Step 1:** Read `cicd-devsecops/SKILL.md` in full before editing.

**Step 2:** Add to SKILL.md (move deep content to references to stay ≤ 500 lines):
- **Secrets Lifecycle** — Vault AppRole auth, dynamic DB credentials, PKI engine, key rotation runbook
- **Compliance Controls** — ISO 27001 control mapping, PCI-DSS requirements, audit evidence checklists
- **Container Runtime Security** — Falco rules, OPA/Gatekeeper admission policies, distroless base images

**Step 3:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py cicd-devsecops
git add cicd-devsecops/
git commit -m "feat: enhance cicd-devsecops — Vault lifecycle, ISO 27001, container runtime security"
```

---

## Success Gate

- [ ] `cloud-architecture` passes validator, SKILL.md ≤ 500 lines, portable metadata present
- [ ] `cicd-pipelines` passes validator, SKILL.md ≤ 500 lines, portable metadata present
- [ ] `cicd-devsecops` still passes validator after enhancement
- [ ] No `Required Plugins` blockers in any of the three — only `Platform Notes`

---

## Reading Material

| Priority | Resource | Format | Cost | Unlocks |
|----------|----------|--------|------|---------|
| 1 | *Docker Deep Dive* — Nigel Poulton | Book | ~$35 | `cloud-architecture` Docker sections |
| 2 | *The DevOps Handbook* — Kim, Humble, Debois, Willis | Book | ~$40 | CI/CD culture and DORA metrics |
| 3 | *Continuous Delivery* — Humble & Farley | Book | ~$50 | Pipeline design theory |
| 4 | AWS Well-Architected Framework | Free PDF (aws.amazon.com/architecture) | Free | AWS patterns and pillars |
| 5 | GitHub Actions documentation | Free (docs.github.com/actions) | Free | Workflow YAML reference |
| 6 | HashiCorp Vault documentation | Free (developer.hashicorp.com/vault/docs) | Free | Vault operations depth |
| 7 | Fastlane documentation | Free (docs.fastlane.tools) | Free | iOS/Android automation |

**Read first:** *Docker Deep Dive* → write skill from it. Then AWS Well-Architected (free).

---

*Next → `phase-02-revenue-infrastructure.md`*
