# World-Class Software Development Engine — Roadmap Index

**Started:** April 2026 | **Scope:** 10 phases, ~200+ skills | **Target:** 2040s-relevant execution engine

---

## What This Roadmap Builds

A fully dual-compatible skills library (Claude Code + Codex) that powers an independent technology business through:
- Consulting practice (AI-differentiated, world-class execution)
- SaaS products (multi-tenant, AI-powered, production-grade)
- Technology grants (East Africa + global institutions)
- Licensing and white-labelling (one codebase, many clients)

All 10 phases build skills — not products. The engine produces the capability. You direct it.

---

## Dual-Compatibility Baseline (Required in Every Phase)

Every `SKILL.md` created or updated must carry:

```yaml
metadata:
  portable: true
  compatible_with: [claude-code, codex]
```

And must contain all eight sections:
```
Use When → Do Not Use When → Required Inputs →
Workflow → Quality Standards → Anti-Patterns → Outputs → References
```

Optional Claude Code features go in **Platform Notes** — never as `Required Plugins` blockers.

Validate after every skill write:
```bash
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

---

## Phase Summary

| Phase | File | Theme | New Skills | Enhancements | Period |
|-------|------|-------|-----------|--------------|--------|
| 01 | [phase-01-infrastructure-foundation.md](phase-01-infrastructure-foundation.md) | Cloud + CI/CD | cloud-architecture, cicd-pipelines | cicd-devsecops | 2026 Q2 |
| 02 | [phase-02-revenue-infrastructure.md](phase-02-revenue-infrastructure.md) | Payments | stripe-payments, subscription-billing | — | 2026 Q2–Q3 |
| 03 | [phase-03-platform-engineering.md](phase-03-platform-engineering.md) | K8s + IaC | kubernetes-platform, infrastructure-as-code | microservices-architecture-models, cicd-pipeline-design | 2026 Q3 |
| 04 | [phase-04-observability-sre.md](phase-04-observability-sre.md) | Observability | observability-platform | database-reliability, cicd-jenkins-debian | 2026 Q4 |
| 05 | [phase-05-quality-e2e-testing.md](phase-05-quality-e2e-testing.md) | E2E Testing | e2e-testing | advanced-testing-strategy | 2026 Q4 |
| 06 | [phase-06-mobile-pwa-completeness.md](phase-06-mobile-pwa-completeness.md) | Mobile + PWA | android-ai-ml, pwa-offline-first | ios-ai-ml | 2027 Q1 |
| 07 | [phase-07-library-maintenance.md](phase-07-library-maintenance.md) | Maintenance | — (3 stubs completed) | webapp-gui-design, pos-restaurant-ui-standard, inventory-management, microservices-communication, web-app-security-audit | 2027 Q1 |
| 08 | [phase-08-competitive-moats.md](phase-08-competitive-moats.md) | Growth + Scale | product-led-growth, event-driven-architecture, graphql-patterns, saas-growth-metrics | — | 2027 Q2 |
| 09 | [phase-09-advanced-ai-rag-depth.md](phase-09-advanced-ai-rag-depth.md) | AI Depth | multimodal-ai | ai-rag-patterns, ai-evaluation, ai-agents-tools | 2027 Q2–Q3 |
| 10 | [phase-10-frontier-thought-leadership.md](phase-10-frontier-thought-leadership.md) | Frontier | edge-computing, react-native-advanced, accessibility-wcag, ar-vr-interfaces | library governance | 2028–2040 |

---

## Critical Path

Phases **01 → 02 → 03** must be completed before any real product can be deployed to paying customers. Do not skip ahead.

Phases **04, 05, 06** can be done in parallel once Phase 03 is complete.

Phase **07** (library maintenance) can be done in any order — it has no dependencies.

Phases **08, 09, 10** compound everything that came before.

---

## Skills Count Trajectory

| After Phase | New Skills Added | Enhancements | Running Total (est.) |
|-------------|-----------------|--------------|----------------------|
| Start | — | — | 176 |
| Phase 01 | 2 | 1 | 178 |
| Phase 02 | 2 | — | 180 |
| Phase 03 | 2 | 2 | 182 |
| Phase 04 | 1 | 2 | 183 |
| Phase 05 | 1 | 1 | 184 |
| Phase 06 | 2 | 1 | 186 |
| Phase 07 | 0 (3 stubs completed, 4 deprecated) | 2 | 186 |
| Phase 08 | 4 | — | 190 |
| Phase 09 | 1 | 3 | 191 |
| Phase 10 | 4 | governance | 195+ |

---

## Reading Programme (Master List)

Books in phase priority order. Buy the Phase 01 books before starting Phase 01.

| Phase | Book | Cost |
|-------|------|------|
| 01 | *Docker Deep Dive* — Nigel Poulton | ~$35 |
| 01 | *The DevOps Handbook* — Kim, Humble, Debois, Willis | ~$40 |
| 01 | *Continuous Delivery* — Humble & Farley | ~$50 |
| 02 | *Subscribed* — Tien Tzuo | ~$25 |
| 03 | *Kubernetes in Action* — Marko Luksa (2nd ed.) | ~$55 |
| 03 | *Production Kubernetes* — Rosso et al. | ~$50 |
| 03 | *Terraform: Up & Running* — Brikman (3rd ed.) | ~$50 |
| 03 | *Infrastructure as Code* — Kief Morris (O'Reilly, 2nd ed.) | ~$50 |
| 04 | *Observability Engineering* — Majors, Fong-Jones, Miranda | ~$55 |
| 04 | *Linux System Administration Handbook* — Nemeth et al. | ~$60 |
| 05 | *Testing JavaScript Applications* — Lucas da Costa | ~$50 |
| 06 | *Building Progressive Web Apps* — Tal Ater | ~$40 |
| 08 | *Product-Led Growth* — Wes Bush | ~$25 |
| 08 | *Building Event-Driven Microservices* — Adam Bellemare | ~$45 |
| 08 | *Hacking Growth* — Sean Ellis & Morgan Brown | ~$25 |
| 08 | *Learning GraphQL* — Porcello & Banks | ~$40 |
| 09 | *AI Engineering* — Chip Huyen (O'Reilly, 2025) | ~$60 |
| 09 | *Hands-On Large Language Models* — Alammar & Grootendorst | ~$60 |
| 09 | *AI-Powered Search* — Trey Grainger (Manning) | ~$55 |

**Free resources that replace books (do not buy what is free):** AWS Well-Architected Framework, Stripe Billing docs, GitHub Actions docs, Playwright docs, Workbox docs, Android ML Kit docs, SigNoz docs, RAGAS docs, WCAG 2.2 spec, Cloudflare Workers docs, Google SRE Book (sre.google/books).

---

## Quarterly Governance (Phase 10 onwards)

After Phase 10, run the governance checklist every quarter:
1. `quick_validate.py` across all skills — fix regressions
2. Check portable metadata on new skills
3. Update time-sensitive content (frontier skills)
4. Deprecate superseded skills
5. Run `upgrade_dual_compat.py` for any new skills missing the portable contract
