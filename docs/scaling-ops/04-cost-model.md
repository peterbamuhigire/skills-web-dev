# Cost Model

**VPS vs cloud cost comparison, Backblaze B2 vs S3, Cloudflare free value, projections**

---

## Current vs Target Infrastructure Cost

### Current State (2 VPS servers)

Estimated based on typical VPS pricing for LAMP monoliths:

| Server | Spec | Provider | Cost/month |
|--------|------|----------|-----------|
| Staging VPS | ~2 vCPU, 4GB RAM | Various | €5–10 |
| Production VPS | ~4 vCPU, 8GB RAM | Various | €8–20 |
| **Total** | | | **€13–30/month** |

### Target State — Step 2 (Web + DB split, Dockerised)

| Server | Spec | Provider | Cost/month |
|--------|------|----------|-----------|
| Web VPS (production) | CX42: 8 vCPU, 16GB | Hetzner | €11.09 |
| DB VPS (production) | CX32: 4 vCPU, 8GB | Hetzner | €5.99 |
| Staging VPS | CX22: 2 vCPU, 4GB | Hetzner | €3.79 |
| Backblaze B2 (files + backups) | ~100GB | Backblaze | €0.60 |
| Cloudflare (WAF + CDN) | Free plan | Cloudflare | €0 |
| **Total** | | | **~€21/month** |

At €21/month, your studio runs world-class infrastructure for the cost of a dinner out.

### Medic8 Addition — Step 3

| Server | Spec | Provider | Cost/month |
|--------|------|----------|-----------|
| Medic8 Web VPS | CX42: 8 vCPU, 16GB | Hetzner | €11.09 |
| Medic8 DB VPS | CX32: 4 vCPU, 8GB | Hetzner | €5.99 |
| B2 (Medic8 patient data) | ~50GB | Backblaze | €0.30 |
| **Medic8 addition** | | | **~€17/month** |
| **Total studio infra** | | | **~€38/month** |

---

## VPS vs Cloud: The Real Cost Comparison

### Compute (Web Server equivalent)

| Option | Spec | Cost/month | Notes |
|--------|------|-----------|-------|
| Hetzner CX42 | 8 vCPU, 16GB | €11 | VPS |
| DigitalOcean 4GB | 2 vCPU, 4GB | $24 | VPS |
| AWS EC2 t3.xlarge | 4 vCPU, 16GB | ~$120 | Cloud |
| AWS EC2 m5.large | 2 vCPU, 8GB | ~$70 | Cloud |
| GCP n2-standard-4 | 4 vCPU, 16GB | ~$135 | Cloud |

**Hetzner gives you 4–10x more compute per euro than AWS/GCP.**

### Database

| Option | Spec | Cost/month | Notes |
|--------|------|-----------|-------|
| Hetzner CX32 (self-managed) | 4 vCPU, 8GB | €6 | Full control |
| PlanetScale Hobby | 5GB | $0 | Managed, limited |
| PlanetScale Scaler | 10GB + branching | $39 | Managed |
| AWS RDS MySQL t3.medium | 2 vCPU, 4GB | ~$60 | Managed |
| AWS RDS MySQL m5.large | 2 vCPU, 8GB | ~$140 | Managed |

Self-managed MySQL on Hetzner wins on cost. You pay with your time (backups, updates).
The `mysql-administration` skill covers everything you need to self-manage MySQL safely.

### File Storage (per TB/month)

| Option | Cost/TB/month | Egress | Notes |
|--------|--------------|--------|-------|
| Backblaze B2 | $6 | Free via Cloudflare | Best value |
| Wasabi | $7 | Free | No egress fees |
| AWS S3 | $23 | $90/TB | Expensive egress |
| GCP Cloud Storage | $20 | $80–120/TB | Expensive egress |
| DigitalOcean Spaces | $21 (250GB min) | $10/TB | Predictable |

**Use Backblaze B2 + Cloudflare.** Free egress via Cloudflare Bandwidth Alliance.

### Cloudflare Free Tier — What You Get for €0

Cloudflare Free replaces services that would cost hundreds per month on AWS:

| Cloudflare Free | AWS Equivalent | AWS Cost/month |
|----------------|----------------|---------------|
| WAF (basic rules) | AWS WAF | $20+ |
| DDoS mitigation | AWS Shield Standard | $3,000/month for Advanced |
| CDN (unlimited bandwidth) | CloudFront | $85/TB |
| SSL certificates | ACM | $0 (but ALB is $16+) |
| DNS (unlimited queries) | Route 53 | $0.40/million |
| Bot Fight Mode | AWS Bot Control | $10+ |
| Analytics (basic) | CloudWatch | $3+ |

**Cloudflare Free is worth $200–300+/month in equivalent AWS services.**

---

## When Does Cloud Become Worth It?

Cloud makes financial sense when:

1. **Traffic is unpredictable** — you need to scale from 0 to 10,000 concurrent users
   in minutes. VPS can't auto-scale. Cloud can.
   *Signal: viral product launch, marketing campaign with unknown reach*

2. **Multi-region is required** — your users are split across continents and latency matters.
   *Signal: EU + US + East Africa users, <100ms response requirement per region*

3. **Managed services save more than they cost** — if RDS saves you 10 hours/month of
   DBA work and your time is worth $100/hour, RDS at $140/month is worth it.
   *Signal: you're spending 5+ hours/month on DB maintenance*

4. **Compliance certifications** — certain enterprise contracts require AWS SOC2 or HIPAA
   Business Associate Agreement. Hetzner offers GDPR but not SOC2 BAA.
   *Signal: US enterprise healthcare or government contract*

5. **Revenue justifies the cost** — cloud ops costs should be < 5% of revenue.
   At $5,000 MRR → $250 cloud budget. At $50,000 MRR → $2,500 cloud budget.

---

## Scaling Cost Projections

### Studio Infrastructure by Phase

| Phase | Monthly VPS Cost | Monthly Tools | Total Infra | Notes |
|-------|-----------------|---------------|-------------|-------|
| Now | €15–30 | €0 | €30 | 2 LAMP VPS |
| Step 1–2 | €21 | €0 | €21 | Web + DB split, Cloudflare free |
| + Medic8 | €38 | €0 | €38 | Dedicated healthcare VPS |
| 3 products | €55 | €0 | €55 | One more web VPS added |
| 5 products | €85 | €5 | €90 | Cloudflare LB ($5) added |
| Scale (10k users/product) | €150 | €20 | €170 | Second web server + Redis |

At €170/month total infrastructure, your studio can serve 50,000+ active users
across 5 products. That represents $50,000–200,000 MRR on negligible infra cost.

### AI API Costs (Additional)

AI API costs scale with usage, not infrastructure:

| Model | Cost per 1M tokens | Typical usage/user/month | Cost per user |
|-------|-------------------|--------------------------|--------------|
| Claude Haiku 4.5 | $1.00 input / $5.00 output | 50K tokens | $0.03–0.15 |
| GPT-4o mini | $0.15 / $0.60 | 50K tokens | $0.01–0.03 |
| DeepSeek V3 | $0.27 / $1.10 | 50K tokens | $0.02–0.05 |

At 1,000 paying tenants, AI costs are manageable at $30–150/month.
See `ai-cost-modeling` and `ai-metering-billing` skills for per-tenant billing.

---

## Summary: The VPS Advantage

At your stage, VPS gives you:

- **10x cost efficiency** vs AWS/GCP for equivalent compute
- **Full control** — no cloud vendor lock-in
- **Predictable billing** — no surprise egress charges
- **GDPR compliance** via Hetzner EU data centres
- **Sufficient scale** for 50,000+ users before cloud becomes necessary
- **Skills transferable** — Linux skills you build work on any cloud later

Cloud is not better infrastructure. It's infrastructure with different trade-offs.
At sub-$50k MRR per product, VPS wins on every dimension that matters to you.
