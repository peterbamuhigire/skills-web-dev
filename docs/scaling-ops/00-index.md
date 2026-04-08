# Scaling & Ops — Index

**Infrastructure strategy for a world-class software studio built on VPS**
**April 2026 | 2 VPS servers (staging + production) | LAMP stack | Multi-tenant SaaS**

---

## The Verdict

VPS-first is the right strategy. Not as a compromise — as a deliberate choice.

Hetzner CX51 (8 vCPU, 32GB RAM): €17/month.
AWS equivalent: ~$200/month.

At your stage — solo studio, multi-tenant SaaS, predictable load — VPS gives you
10x the compute per euro and full control over your infrastructure.
Cloud is the right answer when auto-scaling, global multi-region, or a large ops
team justify the cost. None of those apply yet.

---

## Documents in This Section

| File | What It Covers |
|------|---------------|
| [01-vps-evolution-path.md](01-vps-evolution-path.md) | The 4-step evolution from current LAMP monolith to production-grade multi-product infrastructure |
| [02-server-architecture.md](02-server-architecture.md) | Server roles, Nginx reverse proxy, Docker Compose isolation, recommended VPS specs and providers |
| [03-medic8-compliance.md](03-medic8-compliance.md) | Healthcare SaaS isolation: dedicated VPS, GDPR/data residency, audit logging, encryption at rest |
| [04-cost-model.md](04-cost-model.md) | VPS vs cloud cost comparison, Backblaze B2 vs S3, Cloudflare free tier value, scaling cost projections |
| [05-security-hardening.md](05-security-hardening.md) | Linux hardening, SSH keys, UFW firewall, fail2ban, automatic updates, Nginx security headers |
| [06-backup-disaster-recovery.md](06-backup-disaster-recovery.md) | MySQL backup strategy, off-server storage (Backblaze B2), restore procedures, RTO/RPO targets |

---

## Quick Reference: Current vs Target State

```
CURRENT STATE
─────────────
Staging VPS          Production VPS
(LAMP monolith)      (LAMP monolith)
Everything on        Everything on
one machine          one machine

TARGET STATE (Step 4)
─────────────────────
Cloudflare (WAF + CDN + DDoS — free)
         │
    Load Balancer
    (Nginx, same box as web)
         │
    ┌────┴────┐
    │         │
Web VPS 1   Web VPS 2      Medic8 VPS
(App server) (App server)  (dedicated,
                            compliance)
         │
    DB VPS
    (MySQL, isolated)
         │
    Backblaze B2
    (file storage + backups)
```

---

## Priority Order

1. **Now:** Add Cloudflare in front (free, immediate security and CDN win)
2. **Step 1:** Split DB to its own VPS — removes single point of failure
3. **Step 2:** Dockerise apps — isolation between products on same server
4. **Step 3:** Medic8 gets dedicated VPS — compliance before launch
5. **Step 4:** Second web server + load balancer when traffic justifies it

*Review this strategy when any product hits $20k MRR/month — that's the signal
to evaluate whether cloud makes sense for that specific product.*
