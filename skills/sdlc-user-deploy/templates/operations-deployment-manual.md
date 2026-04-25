# Operations / Deployment Manual Template

**Back to:** [SKILL.md](../SKILL.md)
**Related:** [saas-seeder](../../saas-seeder/SKILL.md) (initial bootstrap) | [vibe-security-skill](../../vibe-security-skill/SKILL.md) (security baseline) | [google-play-store-review](../../google-play-store-review/SKILL.md) (Play Store deployment)

## Purpose

Provide complete instructions for deploying, configuring, and managing the software across all environments. This is the primary reference for system administrators and DevOps engineers.

**Audience:** System administrators, DevOps engineers, IT operations

---

## Template

### 1. Document Information

```markdown
# {Product Name} — Operations / Deployment Manual

| Field | Value |
|-------|-------|
| Document Version | {1.0} |
| Date | {YYYY-MM-DD} |
| Product Version | {1.0.0} |
| Target Audience | System administrators, DevOps |
| Prepared By | {Author / DevOps lead} |
```

### 2. System Architecture Overview

```markdown
## System Architecture Overview

### Component Diagram
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTS                               │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ Web       │  │ Android App  │  │ Member Portal      │    │
│  │ Browser   │  │ (Kotlin)     │  │ /memberpanel/      │    │
│  └─────┬─────┘  └──────┬───────┘  └─────────┬──────────┘    │
└────────┼───────────────┼────────────────────┼────────────────┘
         │               │                    │
    ┌────▼───────────────▼────────────────────▼─────┐
    │          Apache / Nginx (HTTPS:443)            │
    │   ┌──────────────────────────────────────┐    │
    │   │   PHP 8.x Application                │    │
    │   │   /public/        (Franchise Admin)   │    │
    │   │   /adminpanel/    (Super Admin)       │    │
    │   │   /memberpanel/   (End User Portal)   │    │
    │   │   /api/           (REST API - JWT)    │    │
    │   └──────────────┬───────────────────────┘    │
    └──────────────────┼────────────────────────────┘
                       │
    ┌──────────────────▼────────────────────────────┐
    │          MySQL 8.x (utf8mb4_general_ci)       │
    │          Row-level isolation: franchise_id     │
    └───────────────────────────────────────────────┘

### Technology Stack
| Layer | Technology | Version |
|-------|-----------|---------|
| Web Server | Apache / Nginx | 2.4+ / 1.24+ |
| Backend | PHP | 8.x (strict typing) |
| Database | MySQL | 8.x |
| Mobile | Kotlin + Jetpack Compose | Latest stable |
| Web UI | Tabler (Bootstrap 5) | Latest |
| Auth (Web) | PHP Sessions + Argon2ID | — |
| Auth (Mobile) | JWT (access + refresh tokens) | — |

### Port and Protocol Requirements
| Service | Port | Protocol | Direction |
|---------|------|----------|-----------|
| HTTPS (web) | 443 | TCP | Inbound |
| HTTP redirect | 80 | TCP | Inbound (redirect to 443) |
| MySQL | 3306 | TCP | Internal only |
| SSH | 22 | TCP | Admin access (restrict by IP) |
```

### 3. Environment Prerequisites

```markdown
## Environment Prerequisites

### Server Requirements

| Env | OS | CPU | RAM | Disk | Web Server | PHP | MySQL |
|-----|----|----|-----|------|-----------|-----|-------|
| Dev | Windows 11 (WAMP) | 2+ cores | 4 GB | 10 GB | Apache 2.4 | 8.x | 8.4.x |
| Staging | Ubuntu 22.04 LTS | 2 vCPU | 4 GB | 40 GB SSD | Apache/Nginx | 8.x | 8.x |
| Production | Debian 12 | 4 vCPU | 8 GB | 80 GB SSD | Apache/Nginx | 8.x | 8.x |

### Domain and SSL
- **Staging:** staging.{domain.com} with Let's Encrypt certificate
- **Production:** {domain.com} with Let's Encrypt or commercial SSL
- **SSL renewal:** Automated via certbot cron job

### DNS Configuration
| Record | Type | Value |
|--------|------|-------|
| {domain.com} | A | {server-ip} |
| www.{domain.com} | CNAME | {domain.com} |
| staging.{domain.com} | A | {staging-ip} |
```

### 4. Installation Guide

**Guidance:** Provide step-by-step for each environment. Commands must be copy-pasteable.

```markdown
## Installation Guide

### Production (Debian VPS)

#### Step 1: Server Preparation
sudo apt update && sudo apt upgrade -y
sudo apt install -y apache2 php8.x php8.x-{mysql,mbstring,xml,curl,zip,gd,intl} \
    mysql-server git composer unzip certbot python3-certbot-apache

#### Step 2: Database Setup
sudo mysql -u root
CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER '{db_user}'@'localhost' IDENTIFIED BY '{strong-password}';
GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'localhost';
FLUSH PRIVILEGES;
EXIT;

#### Step 3: Application Deployment
cd /var/www/html/
git clone {repository-url} {project-name}
cd {project-name}
composer install --no-dev --optimize-autoloader

#### Step 4: Database Schema and Seed Data
mysql -u {db_user} -p {db_name} < database/schema/core-schema.sql
mysql -u {db_user} -p {db_name} < database/schema/seed-data.sql

#### Step 5: Environment Configuration
cp .env.example .env
# Edit .env with production values (see Configuration Reference below)
chmod 600 .env

#### Step 6: File Permissions
sudo chown -R www-data:www-data /var/www/html/{project-name}
sudo chmod -R 755 /var/www/html/{project-name}
sudo chmod -R 775 /var/www/html/{project-name}/storage
sudo chmod -R 775 /var/www/html/{project-name}/uploads

#### Step 7: Virtual Host Configuration (Apache)
# File: /etc/apache2/sites-available/{domain}.conf
<VirtualHost *:443>
    ServerName {domain.com}
    DocumentRoot /var/www/html/{project-name}/public
    <Directory /var/www/html/{project-name}/public>
        AllowOverride All
        Require all granted
    </Directory>
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/{domain}/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/{domain}/privkey.pem
</VirtualHost>

sudo a2ensite {domain}.conf
sudo a2enmod rewrite ssl
sudo systemctl restart apache2

#### Step 8: PHP Configuration
# File: /etc/php/8.x/apache2/php.ini
memory_limit = 256M
upload_max_filesize = 20M
post_max_size = 25M
max_execution_time = 120
date.timezone = Africa/Nairobi

#### Step 9: Verification
# Check web app loads
curl -I https://{domain.com}/sign-in.php
# Expected: HTTP/2 200

# Check database connection
php /var/www/html/{project-name}/healthcheck.php
# Expected: "Database OK, PHP OK, Session OK"
```

### 5. Configuration Reference

```markdown
## Configuration Reference (.env)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| APP_ENV | Environment mode | production | Yes |
| APP_URL | Base URL | https://domain.com | Yes |
| DB_HOST | Database host | localhost | Yes |
| DB_NAME | Database name | saas_production | Yes |
| DB_USER | Database user | saas_user | Yes |
| DB_PASS | Database password | {strong-password} | Yes |
| SESSION_PREFIX | Session variable prefix | myapp_ | Yes |
| PASSWORD_PEPPER | Argon2ID pepper (64+ chars) | {random-string} | Yes |
| COOKIE_ENCRYPTION_KEY | Cookie encryption (32+ chars) | {random-string} | Yes |
| JWT_SECRET | JWT signing secret | {random-string} | Yes (if mobile) |
| JWT_EXPIRY | Access token TTL (seconds) | 900 | Yes (if mobile) |
| SMTP_HOST | Email server | smtp.provider.com | Recommended |
| SMTP_PORT | Email port | 587 | Recommended |
| SMTP_USER | Email username | noreply@domain.com | Recommended |
| SMTP_PASS | Email password | {password} | Recommended |
```

### 6. Deployment Process

```markdown
## Deployment Process

### Code Deployment Workflow
1. **Pull latest code:** `git pull origin main`
2. **Install dependencies:** `composer install --no-dev --optimize-autoloader`
3. **Run migrations:** `mysql -u {user} -p {db} < database/migrations/YYYY-MM-DD-description.sql`
4. **Clear caches:** `php artisan cache:clear` (or equivalent)
5. **Verify:** Run smoke tests (see Post-Deployment Verification)

### Pre-Deployment Checklist
- [ ] All tests pass on staging
- [ ] Database migration tested on staging
- [ ] Rollback procedure documented for this release
- [ ] Backup taken before deployment
- [ ] Stakeholders notified of deployment window
- [ ] Release notes prepared

### Post-Deployment Verification
- [ ] Login page loads (web)
- [ ] Dashboard renders with correct data
- [ ] Create a test record and verify persistence
- [ ] Mobile app connects and authenticates
- [ ] Reports generate correctly
- [ ] Error log is clean (`tail -f /var/log/apache2/error.log`)

### Rollback Procedure
1. Restore code: `git checkout {previous-tag}`
2. Restore database: `mysql -u {user} -p {db} < backups/{timestamp}.sql`
3. Restart services: `sudo systemctl restart apache2`
4. Verify rollback: Run post-deployment checks
5. Notify team of rollback and reason
```

### 7. Android App Deployment

```markdown
## Android App Deployment

### Build Variants
| Variant | API URL | Signing | Play Track |
|---------|---------|---------|------------|
| dev | http://192.168.x.x:8000/api | debug key | — |
| staging | https://staging.domain.com/api | release key | Internal testing |
| prod | https://domain.com/api | release key | Production |

### Staged Rollout Strategy
| Day | Percentage | Action |
|-----|-----------|--------|
| Day 1 | 1% | Deploy, monitor crash rate |
| Day 3 | 5% | Review crash-free rate (target >99.5%) |
| Day 5 | 20% | Check user feedback, ANR rate |
| Day 7 | 50% | Broader monitoring |
| Day 10 | 100% | Full rollout |

> **Reference:** See `google-play-store-review` skill for Play Store compliance checklist.
```

### 8. Multi-Tenant Operations

```markdown
## Multi-Tenant Operations

### Creating a New Tenant
1. Insert into `tbl_franchises` with franchise details
2. Create franchise owner user with `franchise_id` set
3. Assign default permission set to owner role
4. Verify data isolation: query returns only new franchise data
5. Configure tenant-specific settings (branding, modules, limits)

### Tenant Data Isolation Verification
-- Must return 0 rows if isolation is correct:
SELECT * FROM {any_table}
WHERE franchise_id != {expected_franchise_id}
AND id IN (SELECT id FROM {any_table} WHERE franchise_id = {expected_franchise_id});

### Tenant Suspension / Reactivation
- **Suspend:** Set `tbl_franchises.status = 'suspended'`; middleware blocks all access
- **Reactivate:** Set `status = 'active'`; access restored immediately
- **Data retention:** Suspended tenant data is preserved, not deleted
```

### 9. Backup and Recovery

```markdown
## Backup and Recovery

### Database Backup Schedule
| Frequency | Type | Retention | Command |
|-----------|------|-----------|---------|
| Daily (2 AM) | Full dump | 30 days | mysqldump --single-transaction {db} > backup-$(date +%F).sql |
| Weekly (Sun) | Full dump + files | 90 days | Full DB + /uploads/ directory |
| Pre-deploy | Full dump | Until next deploy | Manual before every deployment |

### Recovery Procedures
#### Full Database Restore
mysql -u {user} -p {db} < backups/backup-YYYY-MM-DD.sql

#### File Restore
rsync -av /backup/uploads/ /var/www/html/{project}/uploads/

#### Backup Verification (Monthly)
1. Restore latest backup to a test database
2. Run application health check against test database
3. Verify record counts match production
4. Document test date and result
```

### 10. Monitoring and Security

```markdown
## Monitoring and Alerting

| Metric | Threshold | Alert Method |
|--------|-----------|-------------|
| CPU usage | > 80% for 5 min | Email |
| Disk usage | > 85% | Email + SMS |
| MySQL connections | > 80% of max | Email |
| HTTP 5xx rate | > 1% of requests | Email + SMS |
| SSL certificate expiry | < 14 days | Email |

### Log Management
| Log | Location | Rotation |
|-----|----------|----------|
| Apache access | /var/log/apache2/access.log | Weekly, 12 weeks |
| Apache error | /var/log/apache2/error.log | Weekly, 12 weeks |
| PHP errors | /var/log/php/error.log | Weekly, 8 weeks |
| MySQL slow query | /var/log/mysql/slow.log | Weekly, 4 weeks |
| Application audit | Database audit_trail table | 365 days retention |

## Security Operations
- **Firewall:** Allow only 22 (SSH, IP-restricted), 80, 443
- **Fail2ban:** Enable for SSH and Apache auth
- **Updates:** Monthly security patches; critical patches within 48 hours
- **SSH:** Key-only authentication, disable root login
- **Audit log review:** Weekly review of failed login attempts and privilege changes
```

### 11. Scaling and Disaster Recovery

```markdown
## Scaling Guide

| Trigger | Action |
|---------|--------|
| CPU consistently > 70% | Upgrade VPS (vertical scaling) |
| Database queries > 200ms P95 | Add indexes, optimize queries, increase buffer pool |
| Disk > 80% | Expand storage or archive old data |
| Concurrent users > 500 | Consider load balancer + second web server |
| Static asset load | Configure CDN (Cloudflare or similar) |

## Disaster Recovery

| Metric | Target |
|--------|--------|
| Recovery Time Objective (RTO) | 4 hours |
| Recovery Point Objective (RPO) | 24 hours (daily backup) |

### DR Procedure
1. Provision replacement server (same Debian version)
2. Restore latest backup (database + files)
3. Update DNS to point to new server
4. Verify application functionality
5. Notify stakeholders of recovery status

### DR Testing Schedule
- **Quarterly:** Tabletop exercise (walk through procedure)
- **Annually:** Full recovery test on isolated environment
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| No rollback plan | Failed deploys become multi-hour outages | Document rollback steps for every release |
| Manual deployments to production | Human error, inconsistency, no audit trail | Script deployment steps; use git-based workflow |
| Shared database credentials | Cannot revoke individual access; audit impossible | Per-user or per-service credentials |
| No backup verification | Backups may be corrupt; discovered only during crisis | Test restores monthly |
| Same .env in all environments | Dev settings in production (debug mode, weak keys) | Environment-specific .env files |
| No monitoring | Outages discovered by users, not by team | Set up monitoring with alerts from day one |

## Quality Checklist

- [ ] All 3 environments documented (Windows dev, Ubuntu staging, Debian prod)
- [ ] Every command is copy-pasteable and tested
- [ ] .env configuration reference includes every variable with description
- [ ] Database setup includes schema, seed data, and super admin creation
- [ ] SSL, firewall, and security hardening covered
- [ ] Backup schedule, recovery procedure, and verification process documented
- [ ] Android deployment covers build variants, signing, and staged rollout
- [ ] Multi-tenant operations cover creation, isolation, and suspension
- [ ] Monitoring covers server, application, database, and SSL metrics
- [ ] Rollback procedures documented for every deployment type
- [ ] Disaster recovery has measurable RTO and RPO targets
- [ ] Document stays under 500 lines (split into sub-files if needed)

---

**Back to:** [SKILL.md](../SKILL.md)
