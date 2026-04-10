# Ansible Security Automation for Debian/Ubuntu Fleets

Purpose: Automate security tasks across a Debian/Ubuntu SaaS fleet using Ansible.
Covers hardening, patching, user management, secret rotation, and Jenkins integration.

## Why Ansible for security automation

Ansible is the right tool for fleet-wide security work because it is:

- **Agentless** — only SSH + Python needed on targets. Fewer moving parts, smaller attack surface.
- **Idempotent** — running a playbook twice leaves the host in the same state; safe to rerun nightly.
- **Declarative YAML** — easy to diff, review, and store in git alongside app code.
- **SSH-based** — reuses existing auth and transport; bastion jump hosts work natively.
- **No agent to secure** — unlike Puppet/Chef, no persistent daemon exposing a control socket.
- **Widely audited modules** — `apt`, `ufw`, `sysctl`, `user`, `authorized_key`, `apparmor` are stable.

Trade-off: slower than agent-based tools on huge fleets. For 5–200 Debian/Ubuntu servers this never bites.

## Inventory patterns for security

A clean inventory layout is the foundation of safe automation.

### Static inventory with host groups

```ini
# inventory/production/hosts
[webservers]
web01.prod.example.com
web02.prod.example.com
web03.prod.example.com

[dbs]
db01.prod.example.com ansible_host=10.0.2.11
db02.prod.example.com ansible_host=10.0.2.12

[bastion]
bastion.prod.example.com ansible_host=203.0.113.10

[prod:children]
webservers
dbs
bastion

[prod:vars]
ansible_user=deploy
ansible_python_interpreter=/usr/bin/python3
```

Grouping by role lets you target operations: `ansible-playbook harden.yml --limit webservers`.

### Dynamic inventory from cloud/API

For auto-scaling fleets, use a dynamic inventory plugin (e.g. `amazon.aws.aws_ec2`, `community.digitalocean.do`, or a custom script that queries your CMDB). This ensures freshly-provisioned hosts are picked up automatically.

### ansible_host with SSH config and bastion jumps

When database hosts are behind a bastion, do not expose their SSH directly. Use `ansible_ssh_common_args` with a ProxyJump:

```ini
[dbs:vars]
ansible_ssh_common_args='-o ProxyJump=deploy@bastion.prod.example.com'
```

Or keep the config cleaner in `~/.ssh/config` and let Ansible inherit it:

```
Host bastion.prod.example.com
    User deploy
    IdentityFile ~/.ssh/id_ed25519_prod

Host 10.0.2.*
    User deploy
    ProxyJump bastion.prod.example.com
```

## Securing the Ansible control node

The control node is your most privileged machine. Treat it accordingly.

- **Dedicated host** — hardened VM, CI runner, or Jenkins agent; never a developer laptop.
- **Least privilege** — use a `deploy` user with narrowly-scoped sudoers, not root.
- **Vault-managed creds** — secrets in Ansible Vault or fetched from HashiCorp Vault at runtime.
- **MFA for human login** — PAM-level MFA (Google Authenticator, hardware key).
- **Network isolation** — admin VLAN only; no public inbound; egress restricted to managed hosts and Vault/git.
- **Audit log** — every `ansible-playbook` invocation logged (who/what/when) and shipped to SIEM.

## Ansible Vault for secrets

Ansible Vault encrypts sensitive variables so they can be committed to git alongside the playbooks that use them.

### Core commands

```bash
# Create a new encrypted file
ansible-vault create group_vars/prod/vault.yml

# Edit an existing encrypted file
ansible-vault edit group_vars/prod/vault.yml

# Encrypt an existing plaintext file
ansible-vault encrypt secrets.yml

# Decrypt to stdout (for CI)
ansible-vault decrypt --output=- secrets.yml

# Re-encrypt with a new password
ansible-vault rekey group_vars/prod/vault.yml

# Encrypt a single string (to paste into a YAML file)
ansible-vault encrypt_string 's3cr3tP@ss' --name 'db_password'
```

### Per-variable encryption with !vault tag

```yaml
# group_vars/prod/main.yml — safe to view in git
db_host: db01.prod.example.com
db_user: app_rw
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  38396361616561613734643435393034...
```

This is preferable to encrypting whole files because diffs remain readable.

### Password file

Store the vault password in a protected file, never on the command line:

```bash
# ~/.vault_pass
pr0dV@ultP@ss
```

```bash
chmod 600 ~/.vault_pass
```

```ini
# ansible.cfg
[defaults]
vault_password_file = ~/.vault_pass
```

### Multiple vault IDs for environment separation

Separate dev/staging/prod passwords so a dev secret leak does not compromise production:

```bash
ansible-playbook site.yml \
  --vault-id dev@~/.vault_pass_dev \
  --vault-id prod@~/.vault_pass_prod
```

## Baseline hardening playbook

A working `harden-debian.yml` applies a baseline to any Debian/Ubuntu host:

```yaml
---
- name: Harden Debian/Ubuntu baseline
  hosts: all
  become: true
  vars:
    admin_user: sysadmin
    admin_ssh_key: "{{ lookup('file', '~/.ssh/id_ed25519_admin.pub') }}"
  tasks:
    - name: Update apt cache
      ansible.builtin.apt: { update_cache: true, cache_valid_time: 3600 }

    - name: Upgrade all packages
      ansible.builtin.apt: { upgrade: dist, autoremove: true }

    - name: Install security essentials
      ansible.builtin.apt:
        name: [ufw, fail2ban, auditd, unattended-upgrades, apparmor, apparmor-utils, libpam-pwquality]
        state: present

    - name: Enable fail2ban
      ansible.builtin.systemd: { name: fail2ban, enabled: true, state: started }

    - name: UFW default deny
      community.general.ufw: { state: enabled, policy: deny, direction: incoming }

    - name: Allow SSH/HTTP/HTTPS
      community.general.ufw: { rule: allow, port: "{{ item }}", proto: tcp }
      loop: [22, 80, 443]

    - name: Harden sshd_config
      ansible.builtin.template:
        src: sshd_config.j2
        dest: /etc/ssh/sshd_config
        mode: "0600"
        validate: "/usr/sbin/sshd -t -f %s"
      notify: restart sshd

    - name: Apply sysctl security baseline
      ansible.posix.sysctl:
        name: "{{ item.name }}"
        value: "{{ item.value }}"
        state: present
        reload: true
      loop:
        - { name: net.ipv4.conf.all.rp_filter,        value: "1" }
        - { name: net.ipv4.conf.all.accept_redirects, value: "0" }
        - { name: net.ipv4.conf.all.send_redirects,   value: "0" }
        - { name: net.ipv4.tcp_syncookies,            value: "1" }
        - { name: kernel.randomize_va_space,          value: "2" }
        - { name: fs.protected_hardlinks,             value: "1" }
        - { name: fs.protected_symlinks,              value: "1" }

    - name: Enable unattended-upgrades
      ansible.builtin.copy:
        content: |
          APT::Periodic::Update-Package-Lists "1";
          APT::Periodic::Unattended-Upgrade "1";
        dest: /etc/apt/apt.conf.d/20auto-upgrades
        mode: "0644"

    - name: Ensure AppArmor enabled
      ansible.builtin.systemd: { name: apparmor, enabled: true, state: started }

    - name: Create admin user
      ansible.builtin.user:
        name: "{{ admin_user }}"
        groups: sudo
        shell: /bin/bash
        create_home: true

    - name: Push admin SSH key
      ansible.posix.authorized_key:
        user: "{{ admin_user }}"
        key: "{{ admin_ssh_key }}"

    - name: Passwordless sudo for admin
      ansible.builtin.copy:
        content: "{{ admin_user }} ALL=(ALL) NOPASSWD:ALL\n"
        dest: "/etc/sudoers.d/90-{{ admin_user }}"
        mode: "0440"
        validate: "visudo -cf %s"

  handlers:
    - name: restart sshd
      ansible.builtin.systemd: { name: ssh, state: restarted }
```

## Role structure

Break reusable hardening into an Ansible role so multiple playbooks can include it:

```
roles/web-hardening/
├── defaults/main.yml          # default variables (overridable)
├── tasks/main.yml             # task entrypoint
├── handlers/main.yml          # restart sshd, reload nginx, etc.
├── templates/sshd_config.j2   # Jinja2 templates
├── files/99-hardening.conf    # static files copied verbatim
└── meta/main.yml              # role metadata and dependencies
```

A playbook then simply imports the role:

```yaml
- hosts: webservers
  become: true
  roles:
    - web-hardening
    - nginx-hardening
```

## Running nightly security patches

A separate, narrow playbook just for apt upgrades, run from cron or Jenkins nightly:

```yaml
---
- name: Nightly security patches
  hosts: all
  become: true
  serial: "25%"
  max_fail_percentage: 10
  tasks:
    - name: apt update
      ansible.builtin.apt:
        update_cache: true

    - name: Install security upgrades only
      ansible.builtin.apt:
        upgrade: safe
        only_upgrade: true

    - name: Check if reboot required
      ansible.builtin.stat:
        path: /var/run/reboot-required
      register: reboot_required

    - name: Reboot if needed
      ansible.builtin.reboot:
        msg: "Nightly patch reboot"
        reboot_timeout: 600
      when: reboot_required.stat.exists
```

Notify on failure by piping Ansible stderr to a Slack/Teams webhook in the cron wrapper.

## Auditing compliance via Ansible

Use check mode to report drift without changing anything:

```bash
ansible-playbook harden-debian.yml --check --diff
```

For deeper audits, write a fact-collection playbook that serialises the host state to JSON and compares it to a baseline file. Store results in a compliance bucket and diff over time.

## Orchestrating user management fleet-wide

Adding, removing, and rotating users is one of the strongest arguments for Ansible.

```yaml
- name: Manage admin users fleet-wide
  hosts: all
  become: true
  vars:
    admins:
      - { name: alice, key: "ssh-ed25519 AAAA...alice", state: present }
      - { name: bob,   key: "ssh-ed25519 AAAA...bob",   state: absent }
  tasks:
    - name: Ensure user account
      ansible.builtin.user:
        name: "{{ item.name }}"
        state: "{{ item.state }}"
        groups: sudo
        shell: /bin/bash
      loop: "{{ admins }}"

    - name: Manage SSH key
      ansible.posix.authorized_key:
        user: "{{ item.name }}"
        key: "{{ item.key }}"
        state: "{{ item.state }}"
      loop: "{{ admins }}"
      when: item.state == 'present'
```

When an admin leaves, flip their entry to `state: absent` and rerun. SSH access is revoked fleet-wide in one command.

## Rotating secrets fleet-wide

When a secret (DB password, API token) needs to be rotated:

1. Generate the new secret and update Vault (Ansible Vault or HashiCorp Vault).
2. Run a playbook that updates the config file on every app host.
3. The playbook's handler restarts the app — zero-downtime if using rolling `serial: 1`.

```yaml
- name: Rotate DB password
  hosts: webservers
  become: true
  serial: 1
  tasks:
    - name: Update app env file
      ansible.builtin.template:
        src: app.env.j2
        dest: /etc/myapp/app.env
        owner: myapp
        mode: "0600"
      notify: restart myapp
  handlers:
    - name: restart myapp
      ansible.builtin.systemd:
        name: myapp
        state: restarted
```

## Deploying TLS certs from a central store

Pull certs from Vault (or a Let's Encrypt renewal host) and deploy to nginx:

```yaml
- name: Deploy TLS certs to nginx
  hosts: webservers
  become: true
  tasks:
    - name: Fetch cert from Vault
      ansible.builtin.set_fact:
        tls_cert: "{{ lookup('community.hashi_vault.hashi_vault', 'secret=secret/data/tls/app.example.com:certificate') }}"
        tls_key: "{{ lookup('community.hashi_vault.hashi_vault', 'secret=secret/data/tls/app.example.com:private_key') }}"

    - name: Write cert
      ansible.builtin.copy:
        content: "{{ tls_cert }}"
        dest: /etc/nginx/tls/app.crt
        mode: "0644"
      notify: reload nginx

    - name: Write private key
      ansible.builtin.copy:
        content: "{{ tls_key }}"
        dest: /etc/nginx/tls/app.key
        mode: "0600"
      notify: reload nginx

    - name: Verify TLS endpoint
      ansible.builtin.shell: |
        echo | openssl s_client -connect localhost:443 -servername app.example.com 2>&1 \
          | openssl x509 -noout -dates
      register: cert_check
      changed_when: false
  handlers:
    - name: reload nginx
      ansible.builtin.systemd:
        name: nginx
        state: reloaded
```

## Integrating with Jenkins

Run Ansible playbooks as Jenkins pipeline stages:

```groovy
stage('Deploy hardening baseline') {
  steps {
    withCredentials([
      sshUserPrivateKey(credentialsId: 'ansible-ssh', keyFileVariable: 'SSH_KEY'),
      file(credentialsId: 'vault-pass', variable: 'VAULT_PASS')
    ]) {
      sh '''
        ansible-playbook -i inventory/production \
          --private-key=$SSH_KEY \
          --vault-password-file=$VAULT_PASS \
          harden-debian.yml
      '''
    }
  }
}
```

Store inventory and vault password as Jenkins credentials (SSH key + Secret file). Never commit them to the pipeline repo.

## Integration with HashiCorp Vault

The `community.hashi_vault` collection lets you fetch secrets at playbook runtime:

```yaml
- name: Fetch DB password from HashiCorp Vault
  ansible.builtin.set_fact:
    db_password: "{{ lookup('community.hashi_vault.hashi_vault',
      'secret=secret/data/myapp/db:password auth_method=approle
       role_id=' + approle_id + ' secret_id=' + approle_secret) }}"
```

AppRole auth is ideal because it works unattended — Jenkins holds the role_id/secret_id as credentials, Vault issues a short-lived token, playbook reads the secret, token expires.

## Safe deployment patterns

Blast-radius control is mandatory for security playbooks:

- `--limit webservers:&prod` — run only on the intersection of groups.
- `serial: 1` — roll changes one host at a time; failures halt the rollout.
- `max_fail_percentage: 10` — abort if more than 10% of hosts fail.
- **Preflight checks** — run a dry `--check` on a canary host before the full run.
- **Tagged tasks** — use `tags` so you can run only SSH hardening: `--tags sshd`.

## Testing playbooks

- **Molecule** — spins up a container/VM, applies the role, runs assertions, tears down. Ideal for CI.
- **ansible-lint** — catches style and safety issues (missing `become`, deprecated syntax, shell without `changed_when`).
- **yamllint** — structural YAML correctness.
- **CI pipeline** — lint + Molecule on every push; full playbook run on merge to main.

## Anti-patterns

- **Plaintext passwords in inventory** — always encrypt with Ansible Vault or fetch from HashiCorp Vault.
- **Running everything as root** — use `become` per task, not at the playbook level where possible, so you can see what actually needs privilege.
- **No change auditing** — always log `ansible-playbook` invocations (user, timestamp, playbook, host pattern) to an immutable store.
- **Playbooks that aren't idempotent** — using `shell:` and `command:` without `creates:` or `changed_when:` leads to drift and flapping.
- **No `--check` run before destructive changes** — always dry-run first on a canary host.
- **Hardcoded host lists in playbooks** — targets belong in inventory, not playbook `hosts:` clauses.
- **No rollback plan** — for every destructive change, have a reverse playbook ready (or a configuration git revert + rerun).

## Cross-references

- `cicd-devsecops/SKILL.md` — parent skill: DevSecOps CI/CD hardening
- `cicd-devsecops/references/vault-secrets-lifecycle.md` — HashiCorp Vault for dynamic secrets
- `cicd-devsecops/references/compliance-mapping.md` — map Ansible-enforced controls to compliance frameworks
- `cicd-jenkins-debian/SKILL.md` — Jenkins pipeline integration
- `linux-security-hardening/SKILL.md` — the hardening baseline Ansible is enforcing
- `network-security/SKILL.md` — firewall and network rules applied via Ansible
