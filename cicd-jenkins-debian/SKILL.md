---
name: cicd-jenkins-debian
description: Set up and configure Jenkins on Debian/Ubuntu — installation, Declarative
  Jenkinsfile patterns, master/agent distributed builds, Docker build agents, plugin
  recommendations, credentials management, and RBAC. Synthesised from CI/CD Pipeline
  Using Jenkins Unleashed (Dingare), CI/CD Pipeline with Docker and Jenkins (Rawat),
  and DevOps Design Patterns (Chintale). Use when installing Jenkins, writing Jenkinsfiles,
  or architecting a self-hosted CI/CD system on Debian/Ubuntu servers.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Jenkins on Debian/Ubuntu

<!-- dual-compat-start -->
## Use When

- Set up and configure Jenkins on Debian/Ubuntu — installation, Declarative Jenkinsfile patterns, master/agent distributed builds, Docker build agents, plugin recommendations, credentials management, and RBAC. Synthesised from CI/CD Pipeline Using Jenkins Unleashed (Dingare), CI/CD Pipeline with Docker and Jenkins (Rawat), and DevOps Design Patterns (Chintale). Use when installing Jenkins, writing Jenkinsfiles, or architecting a self-hosted CI/CD system on Debian/Ubuntu servers.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `cicd-jenkins-debian` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
**Philosophy:** Jenkins controller orchestrates; agents build. The controller never runs builds.
All configuration lives in code (Jenkinsfile in Git) — never in the UI.

---

## 1. Installation (Debian/Ubuntu)

```bash
# Prerequisites
sudo apt update
sudo apt install -y openjdk-17-jdk fontconfig

# Add Jenkins apt repository
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key \
  | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/" \
  | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install -y jenkins

# Start and enable
sudo systemctl enable jenkins
sudo systemctl start jenkins

# Add jenkins user to docker group (required for Docker pipeline steps)
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

Access Jenkins at `http://localhost:8080`. Get initial admin password:
```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

**IMPORTANT:** Put Jenkins behind Nginx with TLS before exposing it beyond localhost.

---

## 2. Architecture: Controller + Agents

```
Jenkins Controller (Debian server)
├── Orchestrates pipelines
├── Stores job configs, credentials, build logs
├── NEVER runs builds (set # of executors = 0 on controller)
│
├── SSH Agent 1 (Debian VM, Java + Docker installed)
├── SSH Agent 2 (Debian VM, Java + Docker installed)
└── Docker Agent (dynamic — spun per build, discarded after)
```

### Adding an SSH Agent

On the **agent machine**:
```bash
sudo apt install -y openjdk-17-jdk docker.io
sudo useradd -m -s /bin/bash jenkins
sudo usermod -aG docker jenkins
# Add Jenkins controller's public key to jenkins user's authorized_keys
```

On the **controller** (Jenkins UI):
`Manage Jenkins → Nodes → New Node → Permanent Agent`
- Remote root directory: `/home/jenkins`
- Launch method: SSH
- Host: agent IP
- Credentials: SSH private key (stored in Jenkins credentials, not filesystem)

### Dynamic Docker Agents

Install the **Docker Pipeline plugin**. In Jenkinsfile:
```groovy
pipeline {
  agent {
    docker {
      image 'maven:3.9-eclipse-temurin-17'
      args '-v /root/.m2:/root/.m2'  // cache Maven deps
    }
  }
  stages { ... }
}
```
Each build runs in a fresh container. No state contamination between builds.

---

## 3. Essential Plugins

Install these immediately after setup:

| Plugin | Purpose |
|---|---|
| Pipeline | Enables Declarative/Scripted pipelines |
| Git | SCM checkout from GitLab/GitHub |
| Docker Pipeline | Run build stages inside Docker containers |
| Credentials Binding | Inject secrets from Jenkins credentials store |
| Role-based Authorization Strategy | Fine-grained RBAC |
| SonarQube Scanner | Code quality gate integration |
| OWASP Dependency-Check | Dependency vulnerability scanning |
| Nexus Artifact Uploader | Push artifacts to Nexus 3 |
| HTML Publisher | Publish security/test reports |
| Slack Notification | Post build status to Slack |
| Timestamper | Add timestamps to console output |
| Build Timeout | Kill hung builds automatically |
| AnsiColor | Colour terminal output in logs |

---

## 4. Declarative Jenkinsfile — Full Pipeline

```groovy
pipeline {
  agent none  // agents declared per stage for isolation

  environment {
    NEXUS_URL     = 'https://nexus.internal'
    SONAR_URL     = 'http://sonar.internal:9000'
    APP_VERSION   = "${env.BUILD_NUMBER}"
    IMAGE_NAME    = "myapp:${env.APP_VERSION}"
  }

  options {
    buildDiscarder(logRotator(numToKeepStr: '30'))
    timeout(time: 45, unit: 'MINUTES')
    ansiColor('xterm')
    timestamps()
  }

  stages {

    stage('Checkout') {
      agent { label 'build-agent' }
      steps {
        checkout scm
      }
    }

    stage('Build') {
      agent { docker { image 'maven:3.9-eclipse-temurin-17' } }
      steps {
        sh 'mvn clean package -DskipTests'
        stash name: 'build-output', includes: 'target/*.jar'
      }
    }

    stage('Tests') {
      parallel {

        stage('Unit Tests') {
          agent { docker { image 'maven:3.9-eclipse-temurin-17' } }
          steps {
            sh 'mvn test'
            junit 'target/surefire-reports/*.xml'
          }
        }

        stage('Lint') {
          agent { docker { image 'checkstyle:latest' } }
          steps {
            sh 'mvn checkstyle:check'
          }
        }
      }
    }

    stage('Security Scan') {
      parallel {

        stage('Dependency Check') {
          agent { label 'build-agent' }
          steps {
            sh 'mvn org.owasp:dependency-check-maven:check'
            publishHTML([
              allowMissing: false,
              reportDir: 'target',
              reportFiles: 'dependency-check-report.html',
              reportName: 'OWASP Dependency Check'
            ])
          }
        }

        stage('SonarQube') {
          agent { label 'build-agent' }
          steps {
            withSonarQubeEnv('SonarQube') {
              sh 'mvn sonar:sonar'
            }
            timeout(time: 5, unit: 'MINUTES') {
              waitForQualityGate abortPipeline: true
            }
          }
        }
      }
    }

    stage('Docker Build + Scan') {
      agent { label 'build-agent' }
      steps {
        unstash 'build-output'
        sh "docker build -t ${IMAGE_NAME} ."
        sh "trivy image --exit-code 1 --severity HIGH,CRITICAL ${IMAGE_NAME}"
      }
    }

    stage('Publish Artifact') {
      agent { label 'build-agent' }
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'nexus-credentials',
          usernameVariable: 'NEXUS_USER',
          passwordVariable: 'NEXUS_PASS'
        )]) {
          sh """
            docker tag ${IMAGE_NAME} ${NEXUS_URL}/docker/${IMAGE_NAME}
            docker login -u ${NEXUS_USER} -p ${NEXUS_PASS} ${NEXUS_URL}
            docker push ${NEXUS_URL}/docker/${IMAGE_NAME}
          """
        }
      }
    }

    stage('Deploy Dev') {
      agent { label 'build-agent' }
      steps {
        sshagent(['ansible-deploy-key']) {
          sh "ansible-playbook -i inventories/dev deploy.yml -e version=${APP_VERSION}"
        }
      }
    }

    stage('Deploy Production') {
      agent { label 'build-agent' }
      when { branch 'main' }
      input {
        message 'Deploy to production?'
        ok 'Deploy'
        submitter 'lead-devs'
      }
      steps {
        sshagent(['ansible-deploy-key']) {
          sh "ansible-playbook -i inventories/prod deploy.yml -e version=${APP_VERSION}"
        }
      }
    }
  }

  post {
    success {
      slackSend channel: '#deployments', color: 'good',
        message: "✓ ${env.JOB_NAME} #${env.BUILD_NUMBER} deployed successfully"
    }
    failure {
      slackSend channel: '#deployments', color: 'danger',
        message: "✗ ${env.JOB_NAME} #${env.BUILD_NUMBER} failed — ${env.BUILD_URL}"
    }
  }
}
```

---

## 5. Credentials Management

**Rule:** Never put passwords, tokens, or keys in Jenkinsfiles or environment variables hardcoded in code.

Store all credentials in `Manage Jenkins → Credentials`:

| Type | Use Case |
|---|---|
| `Username with password` | Nexus, SonarQube, database |
| `SSH Username with private key` | Git checkout, Ansible SSH deploy |
| `Secret text` | API tokens, Slack webhook URLs |
| `Secret file` | kubeconfig, .env files |
| `Certificate` | TLS client certificates |

Reference in pipeline:
```groovy
withCredentials([
  usernamePassword(credentialsId: 'nexus-creds', usernameVariable: 'U', passwordVariable: 'P'),
  sshUserPrivateKey(credentialsId: 'deploy-key', keyFileVariable: 'KEY')
]) {
  sh 'curl -u $U:$P https://nexus.internal/...'
  sh 'ssh -i $KEY deploy@prod.server.internal'
}
```

For higher security, integrate HashiCorp Vault via the **HashiCorp Vault Plugin**:
```groovy
withVault(vaultSecrets: [[path: 'secret/myapp/db', secretValues: [
  [envVar: 'DB_PASS', vaultKey: 'password']
]]]) {
  sh 'deploy-with-db-pass.sh'
}
```

---

## 6. Security Configuration

```
Manage Jenkins → Security → Configure Global Security:
  ✓ Security Realm: Jenkins own user database
  ✓ Disable "Allow users to sign up"
  ✓ Authorization: Role-Based Strategy

Manage Jenkins → Manage and Assign Roles:
  - admin     → all permissions
  - developer → Job/Build, Job/Read, Job/Workspace; no Configure/Delete
  - viewer    → Job/Read only
  - deployer  → Job/Build on production jobs only (separate folder)
```

**Never** give developers the ability to approve their own production deployments.

---

## 7. Backup and Recovery

Three lines of safety:

```bash
# 1. ThinBackup plugin (daily, stored to NFS)
#    Manage Jenkins → ThinBackup → Schedule: 0 2 * * *
#    Backup directory: /mnt/nfs/jenkins-backups

# 2. Rsync JENKINS_HOME to a second server
rsync -avz --delete /var/lib/jenkins/ backup-server:/backups/jenkins/

# 3. Debian snapshot of Jenkins VM (weekly, via your hypervisor)
```

To restore: stop Jenkins, restore JENKINS_HOME contents, start Jenkins.

---

## References

- `references/nginx-reverse-proxy.md` — Nginx TLS config for Jenkins
- `references/multibranch-pipeline.md` — Multibranch pipeline setup for GitLab/GitHub
- `references/shared-library.md` — Jenkins shared library for cross-repo pipeline patterns
