# VPS Evolution Path

**From LAMP monolith to production-grade multi-product infrastructure**
**4 steps — do them in order, only when the previous step is stable**

---

## Where You Start

```
Staging VPS              Production VPS
┌─────────────────┐      ┌─────────────────┐
│ Apache/Nginx    │      │ Apache/Nginx     │
│ PHP             │      │ PHP              │
│ MySQL           │      │ MySQL            │
│ Files (local)   │      │ Files (local)    │
└─────────────────┘      └─────────────────┘
```

Single-server LAMP. Everything co-located. This works until:
- DB load contends with web server CPU
- A bug in one app can affect all apps
- Disk fills up with uploaded files
- A server failure takes everything down together

---

## Step 0 — Cloudflare (Do This Today, Free)

Put Cloudflare in front of your production VPS **before doing anything else**.

**What you get for free:**
- WAF (Web Application Firewall) — blocks SQLi, XSS, bot attacks
- DDoS protection (up to 100Gbps mitigation)
- CDN — static assets served from edge, reduces VPS load
- SSL termination — Cloudflare handles HTTPS, your VPS can serve HTTP internally
- Analytics — real traffic data, not just server logs
- Page Rules — redirect www, force HTTPS, cache control

**How to set it up:**
1. Add your domain to Cloudflare (free plan)
2. Point your domain's nameservers to Cloudflare's
3. Enable "Proxied" (orange cloud) for your A records
4. Set SSL/TLS mode to "Full (strict)"
5. Enable "Always Use HTTPS"
6. Turn on "Bot Fight Mode" under Security

**Ongoing cost:** €0/month (Cloudflare Free is genuinely comprehensive)

---

## Step 1 — Split the Database

Move MySQL to its own VPS. Web and DB on separate machines.

```
Cloudflare
     │
Production Web VPS          Production DB VPS
┌──────────────────┐        ┌──────────────────┐
│ Nginx            │        │ MySQL 8           │
│ PHP apps         │──────► │ (private network) │
│ Local file cache │        │ Automated backups │
└──────────────────┘        └──────────────────┘
```

**Why this matters:**
- Web and DB no longer compete for RAM and CPU
- DB can be sized independently (more RAM = better MySQL performance)
- DB failure doesn't kill the web server (can show maintenance page)
- Web server failure doesn't risk DB data
- Enables adding a second web server later (Step 4) without touching DB

**Implementation notes:**
- Use private networking between servers (Hetzner, DigitalOcean both offer this free)
- Bind MySQL to private IP only (`bind-address = 10.x.x.x`) — never expose to public
- Create a dedicated MySQL user per app with least-privilege grants
- Set up automated MySQL dumps to Backblaze B2 (see [06-backup-disaster-recovery.md](06-backup-disaster-recovery.md))

**Recommended spec for DB VPS:**
- Hetzner CX31: 2 vCPU, 8GB RAM, 80GB SSD — €8.49/month
- Or CX41 (4 vCPU, 16GB RAM) if you have 10+ active tenants

---

## Step 2 — Docker Compose Per Product

Containerise each product on the web VPS. Isolation without cloud migration.

```
Web VPS
┌─────────────────────────────────────────────────────┐
│  Nginx (reverse proxy — port 80/443)                │
│       │              │              │               │
│  [medic8-app]   [saas-product-2]  [saas-product-3]  │
│  Docker network  Docker network   Docker network    │
│  (isolated)      (isolated)       (isolated)        │
└─────────────────────────────────────────────────────┘
```

**Why Docker, not just separate folders:**
- PHP process crash in one app cannot affect others
- Different PHP versions per product (PHP 8.1 for one, 8.3 for another)
- `docker compose up/down` per product — deploy without touching neighbours
- Resource limits per container (prevent one app starving others)
- Reproducible: staging = production, no "works on my machine"

**Nginx reverse proxy pattern:**
```nginx
# /etc/nginx/sites-available/medic8
server {
    server_name medic8.yourdomain.com;
    location / {
        proxy_pass http://localhost:8081;  # Medic8 container port
    }
}

# /etc/nginx/sites-available/saas-product-2
server {
    server_name app2.yourdomain.com;
    location / {
        proxy_pass http://localhost:8082;  # Product 2 container port
    }
}
```

**Docker Compose structure per product:**
```
/srv/
├── medic8/
│   ├── docker-compose.yml
│   ├── .env                  ← secrets, never committed
│   └── app/                  ← PHP source
├── saas-product-2/
│   ├── docker-compose.yml
│   └── app/
```

---

## Step 3 — Medic8 Gets Its Own VPS

Healthcare data requires isolation before you launch to paying clients.

```
Cloudflare
     │
     ├──► Web VPS (all other SaaS products)
     │         │
     │    DB VPS (shared)
     │
     └──► Medic8 Web VPS (dedicated)
               │
          Medic8 DB VPS (dedicated, encrypted at rest)
```

- Dedicated VPS = no shared resources with non-healthcare workloads
- Separate MySQL instance = tenant data physically isolated
- Enables: audit logging per GDPR, data residency guarantee (EU servers)
- Hetzner Finland or Germany = GDPR-compliant EU data centre

See [03-medic8-compliance.md](03-medic8-compliance.md) for full compliance requirements.

**When to do this:** Before Medic8 goes live with real patient/clinic data.

---

## Step 4 — Second Web Server + Load Balancer

Add horizontal scale when traffic justifies it. Do NOT do this prematurely.

```
Cloudflare (with Load Balancing — $5/month add-on)
         │
    ┌────┴────┐
    │         │
Web VPS 1   Web VPS 2
(primary)   (secondary)
    │         │
    └────┬────┘
         │
      DB VPS
```

**Signal to do this:** Production web VPS consistently above 70% CPU, or
any single product exceeds 500 concurrent users.

**Load balancer options (cheapest first):**
1. **Cloudflare Load Balancing** — $5/month, simplest, handled at edge
2. **HAProxy on DB VPS** — $0 software, one extra VPS not needed
3. **Nginx upstream on a third VPS** — full control, ~€5/month extra server

**Session handling:** Use Redis for PHP sessions so any web server can serve any request:
```
Web VPS 1 ──► Redis VPS (shared session store)
Web VPS 2 ──►
```

---

## What Triggers a Cloud Migration?

VPS stays the right answer until **one of these is true** for a specific product:

| Signal | Action |
|--------|--------|
| Needs to scale from 0 to 10,000 users in minutes (viral launch) | Cloud burst capacity for that product |
| Requires multi-region (EU + US + Africa simultaneously) | Cloud for that product |
| Product hits $50k+ MRR and ops cost > 5% of revenue | Evaluate cloud ROI for that product |
| Compliance requires specific certifications (HIPAA, SOC2) the VPS provider can't supply | Cloud for that product |
| Ops burden exceeds 10 hours/week per server | Managed DB + managed hosting |

**Key principle:** Migrate products individually, not the whole studio.
The other products stay on VPS. Only the one product that hits the signal moves.
