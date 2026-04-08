# Medic8 Healthcare Compliance

**Dedicated VPS isolation, GDPR, data residency, encryption, audit logging**

---

## Why Healthcare Needs Separate Infrastructure

Healthcare SaaS is different from other verticals. Before any real clinic or patient
data touches your servers, the following must be true:

1. **Physical isolation** — no shared server with non-healthcare workloads
2. **Data residency** — patient data stays in a specific geographic region
3. **Encryption at rest** — disk encryption on the server
4. **Encryption in transit** — TLS everywhere, internal and external
5. **Audit logging** — every data access logged and tamper-evident
6. **Backup + retention** — defined backup windows, tested restores, retention policy
7. **Access control** — SSH key only, no passwords, minimal admin access

---

## Infrastructure Layout for Medic8

```
Cloudflare (WAF + DDoS + TLS termination)
     │
     ▼
[Medic8 Web VPS — Hetzner Germany/Finland]
  Dedicated server — no shared workloads
  Docker: medic8-app, medic8-nginx
  Encrypted disk (LUKS or Hetzner encrypted volumes)
  UFW firewall: 80/443 only inbound
  Fail2ban on SSH
     │
  Private network (10.x.x.x) — not internet-routable
     │
     ▼
[Medic8 DB VPS — Hetzner Germany/Finland]
  MySQL 8 — dedicated instance
  Bind to private IP only
  Encrypted at rest
  Daily encrypted dumps → Backblaze B2 (EU bucket)
  Weekly full backup → second EU bucket (different region)
```

**Both servers must be in the same Hetzner region** (e.g., both in Falkenstein, Germany)
to use private networking. Germany = GDPR-compliant EU data centre.

---

## GDPR Requirements for Healthcare SaaS in East Africa

East Africa context: Uganda's DPPA 2019 applies if you process personal data
of Ugandan residents. EU GDPR applies if any EU residents' data is processed,
or if you want to sell to EU-funded health projects (very common in the region).

**What this means practically:**

| Requirement | Implementation |
|-------------|---------------|
| Lawful basis for processing | Document in Privacy Policy (consent or legitimate interest) |
| Data minimisation | Don't collect patient fields you don't use |
| Right to erasure | Implement soft-delete with purge functionality |
| Data breach notification (72h) | Set up error alerting + have an incident procedure |
| Data Processing Agreement | Sign with Hetzner (they offer this for EU compliance) |
| No transfer outside region without safeguards | Don't send patient data to OpenAI/Claude without anonymising |

See the `dpia-generator` skill for generating a Data Protection Impact Assessment
and the `uganda-dppa-compliance` skill for Uganda-specific requirements.

---

## Encryption at Rest

### Option 1 — Hetzner Encrypted Volumes (Simplest)

Hetzner Cloud volumes support encryption. Mount your MySQL data directory on an
encrypted volume:

```bash
# Create encrypted volume in Hetzner console, then mount
sudo mkfs.ext4 /dev/sdb
sudo mkdir -p /mnt/mysql-data
sudo mount /dev/sdb /mnt/mysql-data

# Update MySQL data directory
sudo systemctl stop mysql
sudo mv /var/lib/mysql /mnt/mysql-data/
sudo ln -s /mnt/mysql-data/mysql /var/lib/mysql
sudo systemctl start mysql
```

### Option 2 — LUKS Full Disk Encryption (More Thorough)

For a dedicated (bare metal) Hetzner AX server, set up LUKS at provision time.
Requires entering a passphrase on reboot — automate via Hetzner's rescue system.

---

## Audit Logging

Every patient data access must be logged. Three layers:

### Layer 1 — Application Audit Log (MySQL table)

```sql
CREATE TABLE audit_log (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tenant_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED,
    action VARCHAR(100) NOT NULL,       -- 'patient.view', 'record.update', etc.
    resource_type VARCHAR(100),          -- 'patient', 'appointment', etc.
    resource_id BIGINT UNSIGNED,
    ip_address VARCHAR(45),
    user_agent TEXT,
    data_before JSON,                    -- NULL for reads
    data_after JSON,                     -- NULL for reads
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tenant_created (tenant_id, created_at),
    INDEX idx_resource (resource_type, resource_id)
) ENGINE=InnoDB;
```

**What to log:**
- All reads of patient records (user_id, patient_id, timestamp, IP)
- All creates, updates, deletes (with before/after data)
- All authentication events (login, logout, failed login)
- All export events (PDF export, data download)

### Layer 2 — MySQL General Query Log (Selective)

Enable for sensitive tables only (patient, medical_record):

```sql
-- Enable general log for specific users in production selectively
-- Better: use MySQL audit plugin (MariaDB Audit Plugin is free)
INSTALL PLUGIN server_audit SONAME 'server_audit';
SET GLOBAL server_audit_logging = ON;
SET GLOBAL server_audit_events = 'QUERY_DML';
```

### Layer 3 — Nginx Access Log

```nginx
# /etc/nginx/nginx.conf
log_format detailed '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    '$request_time';

access_log /var/log/nginx/medic8_access.log detailed;
```

Archive Nginx logs to B2 weekly. Retain for 12 months minimum.

---

## AI Feature Constraints for Healthcare

When using AI (Claude, GPT-4, etc.) in Medic8:

**Never send to external AI APIs:**
- Patient names, national IDs, phone numbers
- Medical record numbers
- Diagnosis codes linked to identifiable individuals
- Appointment data that identifies a patient

**Safe to send:**
- Aggregated, de-identified statistics ("35-year-old male with symptoms X")
- Anonymised data with all direct identifiers removed
- Synthetic data for testing/training

**Implementation pattern:**
```php
// Strip PII before sending to AI
function anonymiseForAI(array $patientData): array {
    unset($patientData['name'], $patientData['phone'], 
          $patientData['national_id'], $patientData['email']);
    $patientData['age'] = floor($patientData['age'] / 5) * 5; // Round to 5-year band
    return $patientData;
}
```

See `ai-security` skill for full PII scrubbing patterns.

---

## Backup and Retention Policy

| Data Type | Backup Frequency | Retention | Storage |
|-----------|-----------------|-----------|---------|
| MySQL full dump | Daily at 02:00 | 30 days | Backblaze B2 EU |
| MySQL binary logs | Hourly | 7 days | B2 EU |
| Uploaded files (scans, reports) | Real-time sync | Indefinite | B2 EU |
| Audit logs | Daily archive | 5 years | B2 EU cold |
| Application logs | Weekly archive | 12 months | B2 EU |

**Recovery Time Objective (RTO):** < 4 hours
**Recovery Point Objective (RPO):** < 1 hour (binary logs)

Test a full restore quarterly. Document the restore procedure. A backup you
have never restored is not a backup — it is a hope.

---

## Access Control Checklist

Before Medic8 goes live:

- [ ] SSH key authentication only — `PasswordAuthentication no` in sshd_config
- [ ] Root SSH login disabled — `PermitRootLogin no`
- [ ] UFW firewall: allow only 22 (from your IP), 80, 443
- [ ] fail2ban installed and configured (ban after 5 failed SSH attempts)
- [ ] MySQL root password set, test accounts removed, anonymous user removed
- [ ] All app DB connections use dedicated least-privilege user
- [ ] No `.env` files in web-accessible directories
- [ ] Automatic security updates enabled (`unattended-upgrades`)
- [ ] Cloudflare WAF rules enabled for the domain
- [ ] Audit log table created and tested
- [ ] First backup completed and restore tested
- [ ] Data Processing Agreement signed with Hetzner
- [ ] Privacy Policy published with correct data handling disclosures
