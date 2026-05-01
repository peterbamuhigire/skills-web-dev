# Ansible for Debian/Ubuntu — Deep Reference

## Inventory

```ini
# inventories/prod/hosts.ini
[web]
web1.example.com
web2.example.com

[db]
db1.example.com

[debian:children]
web
db

[debian:vars]
ansible_user=deploy
ansible_python_interpreter=/usr/bin/python3
```

```yaml
# inventories/prod/aws_ec2.yml — dynamic AWS inventory
plugin: amazon.aws.aws_ec2
regions: [eu-west-1]
filters: { tag:Environment: prod }
keyed_groups: [{ key: tags.Role, prefix: role }]
```

## Role layout

The canonical structure produced by `ansible-galaxy init`:

```text
roles/nginx/
  defaults/main.yml      # default vars (lowest precedence)
  vars/main.yml          # role vars (high precedence)
  tasks/main.yml         # the work
  handlers/main.yml      # restart/reload triggers
  templates/             # Jinja2 templates
  files/                 # static files
  meta/main.yml          # role metadata, dependencies
```

## Variable precedence (most-specific wins)

`-e` extra vars > task vars > block vars > role vars (`vars/`) > play vars > host vars > group vars > role defaults (`defaults/`).

## Dependencies in `meta/main.yml`

```yaml
dependencies:
  - role: geerlingguy.security
    vars: { security_ssh_permit_root_login: "no" }
  - role: geerlingguy.firewall
```

Install community content: `ansible-galaxy install geerlingguy.nginx`, `ansible-galaxy collection install amazon.aws community.general`.

## Idempotent role example — nginx with handler

```yaml
# roles/nginx/tasks/main.yml
- name: Ensure nginx is installed
  ansible.builtin.apt:
    name: nginx
    state: present
    update_cache: true
    cache_valid_time: 3600

- name: Deploy nginx site config
  ansible.builtin.template:
    src: site.conf.j2
    dest: /etc/nginx/sites-available/{{ site_name }}.conf
    owner: root
    group: root
    mode: "0644"
  notify: Reload nginx

- name: Enable site
  ansible.builtin.file:
    src: /etc/nginx/sites-available/{{ site_name }}.conf
    dest: /etc/nginx/sites-enabled/{{ site_name }}.conf
    state: link
  notify: Reload nginx

# roles/nginx/handlers/main.yml
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
```

## Idempotency anti-patterns

```yaml
# BAD — always reports changed
- ansible.builtin.shell: mkdir -p /var/cache/app

# GOOD — declarative, idempotent
- ansible.builtin.file: { path: /var/cache/app, state: directory, owner: app, mode: "0750" }

# Command with explicit change status
- ansible.builtin.command: nginx -t
  register: nginx_check
  changed_when: false
  failed_when: "'syntax is ok' not in nginx_check.stderr"
```

Dry-run before prod: `ansible-playbook -i inventories/prod site.yml --check --diff`.

## Baseline Ubuntu hardening playbook

```yaml
- hosts: web
  become: true
  tasks:
    - ansible.builtin.apt: { name: [nginx, ufw, fail2ban, unattended-upgrades], state: latest, update_cache: true, cache_valid_time: 3600 }
    - ansible.builtin.user: { name: deploy, groups: sudo, shell: /bin/bash }
    - ansible.posix.authorized_key: { user: deploy, key: "{{ lookup('file', 'files/deploy.pub') }}" }
    - community.general.ufw: { rule: allow, port: "{{ item }}", proto: tcp }
      loop: [22, 443]
    - community.general.ufw: { state: enabled, policy: deny }
    - ansible.builtin.systemd: { name: nginx, state: started, enabled: true }
```

## Tags for partial runs

```yaml
- name: Deploy nginx site config
  ansible.builtin.template: { src: site.conf.j2, dest: /etc/nginx/sites-available/{{ site_name }}.conf }
  tags: [nginx, config]
```

`ansible-playbook site.yml --tags config` runs only tagged tasks — useful for fast config-only loops.
