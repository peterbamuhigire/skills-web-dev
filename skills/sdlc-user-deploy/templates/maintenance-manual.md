# Maintenance Manual Template

**Back to:** [SKILL.md](../SKILL.md)
**Related:** [operations-deployment-manual.md](operations-deployment-manual.md) (initial setup) | [mysql-best-practices](../../mysql-best-practices/SKILL.md) (database tuning) | [vibe-security-skill](../../vibe-security-skill/SKILL.md) (security ops)

## Purpose

Guide support teams on ongoing maintenance, troubleshooting, and system updates. This is the operational handbook for keeping the system healthy after deployment.

**Audience:** Support engineers, on-call teams, DevOps, system administrators

---

## Template

### 1. Document Information

```markdown
# {Product Name} -- Maintenance Manual

| Field | Value |
|-------|-------|
| Document Version | {1.0} |
| Date | {YYYY-MM-DD} |
| Product Version | {1.0.0} |
| Prepared By | {DevOps lead / Author} |

### Contact List
| Role | Name | Contact | Escalation Level |
|------|------|---------|-----------------|
| DevOps Lead | {Name} | {phone/email} | L1 |
| Backend Lead | {Name} | {phone/email} | L2 |
| Database Admin | {Name} | {phone/email} | L2 |
| Mobile Lead | {Name} | {phone/email} | L2 |
| CTO / Architect | {Name} | {phone/email} | L3 |
```

### 2. System Overview

```markdown
## System Overview

### Component Inventory
| Component | Technology | Location | Dependencies |
|-----------|-----------|----------|-------------|
| Web Application | PHP 8.x + Apache | /var/www/html/{project}/public | MySQL, session store |
| REST API | PHP 8.x (JWT auth) | /var/www/html/{project}/api | MySQL, JWT secret |
| Database | MySQL 8.x | localhost:3306 | Disk storage |
| Cron Jobs | PHP CLI scripts | /var/www/html/{project}/cron | MySQL, email service |
| Android App | Kotlin + Compose | Play Store | REST API |
| File Storage | Local filesystem | /var/www/html/{project}/uploads | Disk space |

### Dependency Map
Web App ──> MySQL Database
REST API ──> MySQL Database
REST API ──> Email Service (SMTP)
Android App ──> REST API
Cron Jobs ──> MySQL Database
Cron Jobs ──> Email Service
All ──> SSL Certificate (Let's Encrypt)
```

### 3. Routine Maintenance Tasks

```markdown
## Routine Maintenance Tasks

### Daily (Automated + Spot Check)
| Task | Command / Action | What to Look For |
|------|-----------------|-----------------|
| Check error logs | tail -100 /var/log/apache2/error.log | PHP Fatal, MySQL connection errors |
| Monitor disk space | df -h | Any partition > 85% |
| Verify backup completion | ls -la /backups/daily/ | Today's backup file exists, size > 0 |
| Review security alerts | Check fail2ban: fail2ban-client status | Banned IPs, brute force attempts |
| Check MySQL process list | mysqladmin processlist | Long-running queries (> 30s) |

### Weekly
| Task | Command / Action | Notes |
|------|-----------------|-------|
| Database optimization | OPTIMIZE TABLE {high-churn tables}; | Run on tables with heavy INSERT/DELETE |
| Log rotation check | ls -la /var/log/apache2/ | Verify logrotate is working |
| Performance review | Check slow query log | Queries > 1s need investigation |
| Pending updates | apt list --upgradable | Note security updates |
| Disk growth trend | du -sh /var/www/html/{project}/uploads/ | Compare to last week |

### Monthly
| Task | Notes |
|------|-------|
| Security patch assessment | Apply OS and PHP security patches on staging first |
| SSL certificate expiry check | certbot certificates -- renew if < 30 days |
| Storage growth analysis | Plot uploads/ and database size trends |
| User access audit | Disable inactive accounts (no login > 90 days) |
| Multi-tenant isolation spot check | Run cross-tenant query verification |
| Backup restore test | Restore to test DB, verify record counts |

### Quarterly
| Task | Notes |
|------|-------|
| Disaster recovery drill | Full restore to isolated environment |
| Performance baseline comparison | Compare response times to previous quarter |
| Capacity planning review | Project storage and traffic growth |
| Security audit | Review firewall rules, SSH keys, access logs |

### Annually
| Task | Notes |
|------|-------|
| Major version upgrade assessment | PHP, MySQL, OS version upgrades |
| Architecture review | Evaluate scaling needs, technical debt |
| SLA performance review | Calculate uptime, response time averages |
```

### 4. Troubleshooting Guide

```markdown
## Troubleshooting Guide

### Diagnostic Methodology
1. **Gather information:** What, when, who, how many affected?
2. **Identify scope:** One user, one tenant, all tenants, entire system?
3. **Find root cause:** Check logs, reproduce, trace the request path
4. **Fix:** Apply the least-disruptive fix first
5. **Verify:** Confirm the fix resolves the issue
6. **Document:** Add to known issues log if novel

### Application Issues

| Symptom | Likely Cause | Diagnostic | Fix |
|---------|-------------|-----------|-----|
| White screen / 500 error | PHP fatal error | tail /var/log/apache2/error.log | Fix PHP error, check .env |
| Slow page loads (> 5s) | Slow DB query or missing index | Enable slow query log, check EXPLAIN | Add index or optimize query |
| Login failures | Session config, expired token | Check session path permissions | Fix session.save_path, restart Apache |
| File upload fails | PHP limits or permissions | Check upload_max_filesize, disk space | Update php.ini, fix permissions |
| "Session expired" loops | Cookie domain mismatch | Check .env COOKIE_DOMAIN | Match cookie domain to actual domain |
| Blank dashboard KPIs | Query returns no data | Check franchise_id in queries | Verify user's franchise_id is set |

### Database Issues

| Symptom | Likely Cause | Diagnostic | Fix |
|---------|-------------|-----------|-----|
| Connection refused | MySQL stopped or max_connections hit | systemctl status mysql, SHOW STATUS LIKE 'Threads_connected' | Restart MySQL or increase max_connections |
| Slow queries (> 1s) | Missing index or full table scan | EXPLAIN {query} | Add composite index, optimize query |
| Deadlocks | Concurrent transactions on same rows | SHOW ENGINE INNODB STATUS | Reorder transaction logic, add retry |
| Migration fails | Syntax error or constraint violation | Read error message, check SQL syntax | Fix SQL, verify data constraints, rollback |
| Disk full | Binary logs or large tables | du -sh /var/lib/mysql/ | Purge old binary logs, archive data |

### Mobile App Issues

| Symptom | Likely Cause | Diagnostic | Fix |
|---------|-------------|-----------|-----|
| API connection failure | Wrong base URL or SSL issue | Check BuildConfig.API_URL, test with curl | Update base URL, fix SSL cert |
| Token refresh loops | Clock skew or revoked token | Check server time, token table | Sync NTP, clear revoked tokens |
| Offline sync conflicts | Same record edited in two places | Check conflict_resolution logic | Server version wins; preserve local as draft |
| App crashes on launch | Samsung Knox + EncryptedSharedPreferences | Check crash logs in Play Console | Wrap init in try-catch, fallback to SharedPreferences |
| Play Store update stuck | Staged rollout paused | Check Play Console rollout status | Resume or increase rollout percentage |

### Infrastructure Issues

| Symptom | Likely Cause | Diagnostic | Fix |
|---------|-------------|-----------|-----|
| Disk full | Logs, uploads, or DB growth | df -h, du -sh /var/log/ /uploads/ | Clean logs, archive old uploads, expand disk |
| Memory exhaustion | PHP processes or MySQL buffer | free -h, top | Reduce max_children, tune buffer pool |
| SSL cert expired | Certbot renewal failed | certbot certificates | certbot renew, check cron |
| DNS not resolving | DNS propagation or config error | dig {domain} | Check DNS records, wait for propagation |
| High CPU | Runaway query or PHP loop | top, mysqladmin processlist | Kill runaway process, fix code |

### Multi-Tenant Issues

| Symptom | Severity | Fix |
|---------|----------|-----|
| Data visible across tenants | P1 CRITICAL | Immediately: add WHERE franchise_id = ? to offending query. Audit all similar queries. |
| Tenant creation fails | P2 | Check franchise insert logic, verify required fields |
| Tenant-specific slow performance | P3 | Check tenant's data volume, add indexes for large tenants |
```

### 5. Troubleshooting Decision Tree

```markdown
### Decision Tree: System Slow or Unresponsive

Is the server reachable? (ping/SSH)
├── NO --> Check hosting provider status, DNS, network
└── YES
    └── Is Apache/Nginx running?
        ├── NO --> sudo systemctl restart apache2
        └── YES
            └── Is MySQL running?
                ├── NO --> sudo systemctl restart mysql, check logs
                └── YES
                    └── Check CPU/Memory (top, free -h)
                        ├── CPU > 90% --> Find process (top), kill if runaway
                        ├── Memory > 90% --> Restart Apache, tune MySQL buffers
                        └── Resources OK
                            └── Check slow query log
                                ├── Slow queries found --> EXPLAIN + add indexes
                                └── No slow queries --> Check network latency, CDN
```

### 6. Incident Management

```markdown
## Incident Management

### Severity Levels
| Level | Name | Criteria | Response Time | Examples |
|-------|------|----------|--------------|---------|
| P1 | Critical | System down, data breach, all tenants affected | 15 minutes | Server crash, data leak, auth bypass |
| P2 | Major | Major feature broken, many tenants affected | 1 hour | Reports not generating, payments failing |
| P3 | Minor | Minor feature broken, workaround exists | 4 hours | UI glitch, non-critical export issue |
| P4 | Low | Cosmetic issue, feature request | Next sprint | Typo, color inconsistency, nice-to-have |

### Incident Response Procedure
1. **Detect:** Alert received or user report
2. **Triage:** Assign severity level (P1-P4)
3. **Communicate:** Notify affected parties (use templates below)
4. **Investigate:** Gather logs, reproduce, identify root cause
5. **Fix:** Apply fix (hotfix for P1/P2, next release for P3/P4)
6. **Verify:** Confirm fix in production
7. **Post-mortem:** Blameless review within 48 hours (P1/P2 only)

### Communication Template (P1/P2)
**Subject:** [{Product}] {Severity} Incident -- {Brief Description}
**To:** {Affected tenant admins}
**Body:**
We are aware of {issue description}. Our team is actively investigating.
Impact: {What is affected}
Status: {Investigating / Identified / Fixing / Resolved}
Next update: {Time}

### Post-Incident Review Template
| Field | Value |
|-------|-------|
| Incident Date | {YYYY-MM-DD HH:MM} |
| Severity | {P1/P2} |
| Duration | {minutes/hours} |
| Root Cause | {What actually caused it} |
| Impact | {Who/what was affected} |
| Resolution | {What fixed it} |
| Action Items | {Prevent recurrence -- specific tasks with owners} |
```

### 7. Patching and Performance Tuning

```markdown
## Patching and Updates

### Security Patch Process
1. Assess: Review patch advisory (severity, affected components)
2. Test: Apply to staging, run full test suite
3. Schedule: Announce maintenance window (P1: immediate, others: planned)
4. Deploy: Apply to production
5. Verify: Run smoke tests, check error logs

## Performance Tuning Quick Reference

### MySQL Tuning (my.cnf)
innodb_buffer_pool_size = 70% of available RAM (e.g., 5G for 8GB server)
innodb_log_file_size = 512M
max_connections = 200
slow_query_log = 1
long_query_time = 1

### PHP Tuning (php.ini)
opcache.enable = 1
opcache.memory_consumption = 128
memory_limit = 256M
max_execution_time = 120
realpath_cache_size = 4096K

### Apache Tuning (mpm_prefork.conf)
StartServers 5
MinSpareServers 5
MaxSpareServers 10
MaxRequestWorkers 150
MaxConnectionsPerChild 3000
```

### 8. Runbooks

```markdown
## Runbooks (Step-by-Step Procedures)

### Runbook: Deploy Hotfix to Production
1. Create branch: git checkout -b hotfix/v{VERSION}
2. Apply fix and commit
3. Test on staging
4. Backup production database
5. Deploy: git pull origin hotfix/v{VERSION}
6. Run migration if needed
7. Verify: smoke tests
8. Merge to main: git merge hotfix/v{VERSION}

### Runbook: Restore Database from Backup
1. Stop application: sudo systemctl stop apache2
2. Restore: mysql -u {user} -p {db} < backups/{file}.sql
3. Verify record counts against backup log
4. Start application: sudo systemctl start apache2
5. Run health check

### Runbook: Create New Tenant
1. INSERT INTO tbl_franchises (name, code, status) VALUES ('{name}', '{code}', 'active')
2. Create owner user with franchise_id = {new_id}
3. Assign default permissions
4. Verify: log in as owner, confirm data isolation
5. Notify tenant admin with credentials

### Runbook: Reset User Password
1. Identify user: SELECT id, email FROM tbl_users WHERE email = '{email}'
2. Use admin panel: Adminpanel > Users > Find user > Reset Password
3. (Or) Use super-user-dev.php in dev environment only
4. Communicate new temporary password securely
5. User must change password on next login
```

### 9. Data Management and Knowledge Base

```markdown
## Data Management

### Data Retention Policies
| Data Type | Retention | Action After |
|-----------|-----------|-------------|
| Active records | Indefinite | Archive on tenant closure |
| Audit logs | 365 days | Archive to cold storage |
| Error logs | 90 days | Delete |
| Backups (daily) | 30 days | Delete |
| Backups (weekly) | 90 days | Delete |
| Deleted records (soft delete) | 90 days | Hard delete |

### Tenant Data Export (Offboarding)
1. Export all tenant tables: WHERE franchise_id = {id}
2. Export uploaded files from /uploads/{franchise_id}/
3. Package as encrypted ZIP
4. Deliver to tenant admin securely
5. After confirmation: purge tenant data (hard delete + backup)

## Knowledge Base

### Where to Find Documentation
| Topic | Location |
|-------|----------|
| Architecture | SDD from sdlc-design |
| Deployment setup | Operations/Deployment Manual |
| User workflows | Software User Manual |
| Database standards | mysql-best-practices skill |
| Security baseline | vibe-security-skill |

### How to Update Runbooks
1. When a procedure changes, update the runbook immediately
2. Add a "Last Tested" date to each runbook
3. Review all runbooks quarterly
4. After any incident: check if a runbook needs updating
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| No runbooks -- rely on tribal knowledge | One person leaves, team is helpless | Write step-by-step runbooks for every procedure |
| No post-incident reviews | Same incidents repeat | Conduct blameless post-mortems for P1/P2 |
| Ignoring logs until crisis | Problems escalate silently | Daily log review as routine task |
| No routine maintenance schedule | Systems degrade over time | Follow the daily/weekly/monthly/quarterly calendar |
| Shared root access | No audit trail, no accountability | Per-user SSH keys, no root login |
| No backup verification | Backups may be corrupt | Test restore monthly |

## Quality Checklist

- [ ] Contact list with escalation paths complete
- [ ] Component inventory with dependencies documented
- [ ] Routine maintenance tasks defined (daily, weekly, monthly, quarterly, annually)
- [ ] Troubleshooting covers application, database, mobile, infrastructure, and multi-tenant
- [ ] At least one decision tree for the most common issue category
- [ ] Incident severity levels defined with response times
- [ ] Incident response procedure and communication templates ready
- [ ] Performance tuning parameters documented for MySQL, PHP, and Apache
- [ ] At least 4 runbooks for most common operational tasks
- [ ] Data retention policies defined
- [ ] Knowledge base links to related documentation
- [ ] Document stays under 500 lines (split into sub-files if needed)

---

**Back to:** [SKILL.md](../SKILL.md)
