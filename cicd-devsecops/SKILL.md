---
name: cicd-devsecops
description: Harden CI/CD pipelines with DevSecOps practices — secrets management (HashiCorp Vault), dependency scanning (OWASP DC), code quality gates (SonarQube), container image scanning (Trivy), RBAC, network hardening, and container security for self-managed Debian/Ubuntu servers. Synthesised from DevOps Design Patterns (Chintale), CI/CD Pipeline with Docker and Jenkins (Rawat), and Learning GitHub Actions (Laster). Use when adding security gates to pipelines, hardening CI servers, or implementing shift-left security.
---

# DevSecOps — CI/CD Security Hardening

**Philosophy:** Shift security left — find and block vulnerabilities in the pipeline before they
reach production. Security is a shared responsibility across every team member, not a separate gate
at the end.

---

## 1. The Five Security Gates

Integrate these five gates into every pipeline, in this order:

```
Gate 1: Static Analysis (SonarQube)        — code quality + security smells
Gate 2: Dependency Scanning (OWASP DC)     — known CVEs in libraries
Gate 3: Docker Image Scanning (Trivy)      — CVEs in base image + installed packages
Gate 4: Dynamic Analysis (OWASP ZAP)       — running app attack simulation (staging only)
Gate 5: Compliance Check (custom scripts)  — CIS benchmarks, policy as code
```

Gates 1–3 run on every commit. Gate 4 runs against staging. Gate 5 runs nightly.

---

## 2. Secrets Management — HashiCorp Vault

**Rule:** No secret ever touches a Jenkinsfile, `.env` file, or environment variable in source code.

### Install Vault on Debian

```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor \
  -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
  https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install -y vault
sudo systemctl enable vault && sudo systemctl start vault
```

### Vault Secret Paths Convention

```
secret/ci/nexus          → { username, password }
secret/ci/sonarqube      → { token }
secret/ci/slack          → { webhook_url }
secret/app/<name>/db     → { host, port, username, password }
secret/app/<name>/api    → { key, secret }
secret/ssh/deploy-key    → { private_key }
```

### Pull Secrets in Jenkins Pipeline

```groovy
withVault(vaultSecrets: [
  [path: 'secret/ci/nexus', secretValues: [
    [envVar: 'NEXUS_USER', vaultKey: 'username'],
    [envVar: 'NEXUS_PASS', vaultKey: 'password']
  ]],
  [path: 'secret/app/myapp/db', secretValues: [
    [envVar: 'DB_PASS', vaultKey: 'password']
  ]]
]) {
  sh 'docker login -u $NEXUS_USER -p $NEXUS_PASS nexus.internal'
}
```

### Dynamic Short-Lived Database Credentials

```bash
# Enable Vault database secrets engine
vault secrets enable database
vault write database/config/myapp \
  plugin_name=mysql-database-plugin \
  connection_url="{{username}}:{{password}}@tcp(db.internal:3306)/" \
  allowed_roles="ci-role" username="vault-admin" password="..."

vault write database/roles/ci-role \
  db_name=myapp \
  creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; GRANT SELECT ON myapp.* TO '{{name}}'@'%';" \
  default_ttl="1h" max_ttl="24h"
```

Each pipeline run gets a unique database user that expires after 1 hour.

---

## 3. SonarQube — Code Quality Gate

### Install SonarQube CE on Debian

```bash
# Prerequisites
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres createuser sonar
sudo -u postgres createdb -O sonar sonarqube

# Download and install
wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-10.x.x.zip
sudo unzip sonarqube-*.zip -d /opt/
sudo useradd -M -d /opt/sonarqube sonar
sudo chown -R sonar:sonar /opt/sonarqube

# systemd service — see references/sonarqube-service.md
sudo systemctl enable sonarqube && sudo systemctl start sonarqube
```

Access at `http://sonar.internal:9000`. Default: `admin/admin` — change immediately.

### Quality Gate Configuration

Create a custom Quality Gate (not the default Sonar Way):

| Condition | Threshold | Action |
|---|---|---|
| Coverage on new code | < 70% | Fail |
| Duplicated lines on new code | > 5% | Fail |
| Maintainability rating on new code | D or worse | Fail |
| Reliability rating on new code | C or worse | Fail |
| Security rating on new code | C or worse | Fail |
| Security hotspots reviewed | < 100% | Fail |

### Jenkins Integration

```groovy
stage('SonarQube Analysis') {
  steps {
    withSonarQubeEnv('SonarQube') {  // configured in Manage Jenkins → SonarQube servers
      sh '''
        mvn sonar:sonar \
          -Dsonar.projectKey=myapp \
          -Dsonar.projectName="My App" \
          -Dsonar.host.url=$SONAR_HOST_URL \
          -Dsonar.login=$SONAR_AUTH_TOKEN
      '''
    }
    timeout(time: 5, unit: 'MINUTES') {
      waitForQualityGate abortPipeline: true  // fails pipeline if gate not passed
    }
  }
}
```

---

## 4. OWASP Dependency-Check

Scans all third-party libraries for known CVEs (NIST National Vulnerability Database).

### Maven Integration

```xml
<!-- pom.xml -->
<plugin>
  <groupId>org.owasp</groupId>
  <artifactId>dependency-check-maven</artifactId>
  <version>9.0.9</version>
  <configuration>
    <failBuildOnCVSS>7</failBuildOnCVSS>  <!-- fail on HIGH+ vulnerabilities -->
    <suppressionFile>owasp-suppressions.xml</suppressionFile>
    <format>HTML</format>
    <outputDirectory>${project.build.directory}</outputDirectory>
  </configuration>
</plugin>
```

### Jenkins Pipeline Stage

```groovy
stage('OWASP Dependency Check') {
  steps {
    sh 'mvn org.owasp:dependency-check-maven:check'
    publishHTML([
      allowMissing: false,
      alwaysLinkToLastBuild: true,
      reportDir: 'target',
      reportFiles: 'dependency-check-report.html',
      reportName: 'OWASP Dependency Check Report'
    ])
  }
}
```

**Suppressions** — for false positives, create `owasp-suppressions.xml`:
```xml
<suppressions>
  <suppress>
    <notes>False positive — library is not used at runtime</notes>
    <cve>CVE-2023-XXXXX</cve>
  </suppress>
</suppressions>
```

---

## 5. Trivy — Container Image Scanning

### Install on Debian Build Agents

```bash
sudo apt install -y wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key \
  | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb \
  $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt update && sudo apt install -y trivy
```

### Jenkins Pipeline Stage

```groovy
stage('Trivy Image Scan') {
  steps {
    sh """
      trivy image \
        --exit-code 1 \
        --severity HIGH,CRITICAL \
        --ignore-unfixed \
        --format template \
        --template "@/usr/local/share/trivy/templates/html.tpl" \
        --output trivy-report.html \
        myapp:${env.BUILD_NUMBER}
    """
    publishHTML([reportDir: '.', reportFiles: 'trivy-report.html', reportName: 'Trivy Scan'])
  }
}
```

`--exit-code 1` fails the pipeline on any HIGH or CRITICAL CVE. `--ignore-unfixed` skips CVEs with no available fix (reduces noise).

---

## 6. Container Security Hardening

### Dockerfile Hardening Checklist

```dockerfile
# Use minimal base image
FROM debian:12-slim

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy only what's needed (multi-stage build — build stage separate)
COPY --chown=appuser:appgroup target/myapp.jar /app/myapp.jar

# Drop all capabilities; add only what's needed
# (enforced at docker run time, not Dockerfile)

# Run as non-root
USER appuser

# Use COPY not ADD (ADD can fetch remote URLs — security risk)
# Don't COPY .git, .env, *.key, *.pem, credentials.json

EXPOSE 8080
CMD ["java", "-jar", "/app/myapp.jar"]
```

### Docker Run Hardening

```bash
docker run \
  --user 1000:1000 \           # non-root UID/GID
  --cap-drop ALL \             # drop all Linux capabilities
  --cap-add NET_BIND_SERVICE \ # add back only what's needed
  --no-new-privileges \        # prevent privilege escalation
  --read-only \                # read-only root filesystem
  --tmpfs /tmp \               # writable temp dir only
  --security-opt no-new-privileges \
  --memory 512m \              # resource limits
  --cpus 0.5 \
  myapp:1.4.2
```

---

## 7. CI Server Network Hardening (Debian)

```bash
# UFW firewall rules for Jenkins server
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 10.0.0.0/8 to any port 22   # SSH from internal network only
sudo ufw allow from 10.0.0.0/8 to any port 8080  # Jenkins from internal only
sudo ufw allow 443                                 # Nginx TLS (public)
sudo ufw allow 80                                  # HTTP (redirect to 443)
sudo ufw enable

# fail2ban — block brute-force SSH
sudo apt install -y fail2ban
sudo systemctl enable fail2ban && sudo systemctl start fail2ban

# Unattended security upgrades
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

**Jenkins must never be exposed directly on port 8080 to the internet.** Use Nginx as a TLS-terminating reverse proxy.

---

## 8. Jenkins RBAC Configuration

Using the **Role-based Authorization Strategy** plugin:

```
Global Roles:
  admin      → Overall/Administer, Run Scripts
  developer  → Overall/Read, Job/Build, Job/Read, Job/Workspace
  viewer     → Overall/Read, Job/Read

Item (Folder) Roles:
  prod-deployer  → Job/Build on /Production/* folder only
  dev-deployer   → Job/Build on /Development/* folder only

Assignment Rules:
  - Developers cannot self-approve production deployments
  - Only lead-devs group can approve production input gate
  - Security team has read-only access to all pipeline reports
```

---

## 9. Pipeline Security Checklist

Before deploying any pipeline to production:

- [ ] No secrets in Jenkinsfile, YAML, or `.env` committed to Git
- [ ] All credentials stored in Jenkins Credentials Manager or Vault
- [ ] SonarQube quality gate is enabled and set to fail on security rating C+
- [ ] OWASP Dependency-Check runs and fails on CVSS ≥ 7
- [ ] Trivy image scan runs and fails on HIGH/CRITICAL CVEs
- [ ] Docker build uses non-root USER in Dockerfile
- [ ] Production deploy requires manual approval from lead-devs role
- [ ] Production deploy triggers only from `main` branch
- [ ] Jenkins master is behind Nginx TLS, port 8080 not publicly accessible
- [ ] SSH keys used for all Jenkins-to-agent and Ansible connections (no passwords)
- [ ] `fail2ban` active on all CI servers
- [ ] `unattended-upgrades` active on all CI servers
- [ ] Jenkins backup runs nightly to off-server location
- [ ] All pipeline reports (Trivy, OWASP, SonarQube) published to Jenkins for audit trail

---

## References

- `references/vault-setup.md` — Full HashiCorp Vault init and unsealing procedure
- `references/sonarqube-service.md` — SonarQube systemd service unit file
- `references/nginx-tls.md` — Nginx reverse proxy config for Jenkins and SonarQube
- `references/owasp-zap-stage.md` — OWASP ZAP DAST integration for staging pipeline
