# Deployment on Debian / Ubuntu

Python services run as systemd units under a dedicated `app` user, using a project-local venv built with `uv`. This is the production baseline for Debian 12 (bookworm) and Ubuntu 22.04/24.04.

## System prep (one-time per host)

```bash
# System packages
apt update
apt install -y python3.12 python3.12-venv python3.12-dev \
               build-essential libffi-dev libssl-dev \
               nginx redis-server logrotate

# Dedicated system user (no shell, no home beyond app tree)
useradd --system --shell /usr/sbin/nologin --home /var/www/myapp-sidecar app

# uv - the installer writes to /usr/local/bin
curl -LsSf https://astral.sh/uv/install.sh | env INSTALL_DIR=/usr/local/bin sh

# Directories
install -d -o app -g app -m 0750 /var/www/myapp-sidecar
install -d -o app -g app -m 0750 /var/app/storage
install -d -o app -g app -m 0750 /var/log/myapp
install -d -o root -g app -m 0750 /etc/myapp
install -d -o app -g app -m 0755 /run/myapp     # pid files, sockets
```

Never install Python packages globally with `pip`. System Python is for the system only.

## Deployment tree

```text
/var/www/myapp-sidecar/
|-- releases/
|   |-- 2026-04-15T10-00-00-abc123/     # git sha suffix
|   |-- 2026-04-15T11-15-00-def456/
|   `-- 2026-04-16T09-00-00-ghi789/
|-- current -> releases/2026-04-16T09-00-00-ghi789/
|-- shared/
|   |-- .venv/                          # only if venv is shared (see below)
|   `-- logs/
```

Two strategies for the venv:

- **Per-release venv** (preferred). Each release directory contains its own `.venv`. Rollback is a symlink flip, no reinstall. Costs disk (~200 MB per release; keep the last 5).
- **Shared venv** in `shared/.venv`. Saves disk but rollback is not atomic — you have to reinstall the old requirements.

Default to per-release. Disk is cheap.

## Install with uv

```bash
# Inside the new release dir, as 'app' user
cd /var/www/myapp-sidecar/releases/2026-04-16T09-00-00-ghi789
uv venv --python 3.12 .venv
uv sync --frozen --no-dev
```

`--frozen` fails the deploy if `uv.lock` is stale — good; lockfile drift should never reach production. `--no-dev` skips test/lint deps.

For wheels with C extensions (numpy, pandas, pillow), uv downloads pre-built wheels from PyPI; you almost never need the build toolchain at deploy time, but `build-essential` is installed just in case a pure-Python dep pulls in a native extension.

## Secrets: env file

Secrets live in `/etc/myapp/sidecar.env`, never in the repo and never in environment variables set at user login.

```bash
install -o root -g app -m 0640 /dev/null /etc/myapp/sidecar.env
# Then write via `tee` / config management
```

Format:

```text
# /etc/myapp/sidecar.env
ENV=prod
LOG_LEVEL=info
DATABASE_URL=mysql+aiomysql://app:REDACTED@127.0.0.1:3306/myapp
REDIS_URL=redis://127.0.0.1:6379/1
INTERNAL_SECRET=REDACTED_64_CHARS
S3_BUCKET=myapp-prod-reports
S3_REGION=eu-west-2
AWS_ACCESS_KEY_ID=REDACTED
AWS_SECRET_ACCESS_KEY=REDACTED
```

Permissions: `0640 root:app`. Readable by the service, not world-readable. `sudo cat /etc/myapp/sidecar.env` is the only way to see it — which you should grep for in audit logs.

For multiple services on the same host, one env file per service (`sidecar.env`, `worker.env`) so you can rotate secrets per service.

## systemd unit: FastAPI sidecar

```ini
# /etc/systemd/system/myapp-sidecar.service
[Unit]
Description=MyApp Python Sidecar
Documentation=https://internal.example.com/docs/myapp-sidecar
After=network-online.target mysql.service redis.service
Wants=network-online.target
PartOf=myapp.target

[Service]
Type=exec
User=app
Group=app
WorkingDirectory=/var/www/myapp-sidecar/current
EnvironmentFile=/etc/myapp/sidecar.env
Environment="PYTHONUNBUFFERED=1"
Environment="PATH=/var/www/myapp-sidecar/current/.venv/bin:/usr/bin"
ExecStartPre=/var/www/myapp-sidecar/current/.venv/bin/python -m service_name.preflight
ExecStart=/var/www/myapp-sidecar/current/.venv/bin/uvicorn service_name.main:app \
    --host 127.0.0.1 --port 8001 \
    --workers 2 \
    --proxy-headers \
    --forwarded-allow-ips='127.0.0.1' \
    --timeout-keep-alive 5 \
    --timeout-graceful-shutdown 25 \
    --log-config /etc/myapp/log_config.json
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5s
TimeoutStopSec=30
KillMode=mixed

# Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/app/storage /var/log/myapp /run/myapp
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictNamespaces=true
LockPersonality=true
RestrictRealtime=true
SystemCallArchitectures=native
CapabilityBoundingSet=

# Resource limits
LimitNOFILE=65536
MemoryMax=1G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

The hardening stanza is copy-paste across services. Review each field before removing — most are free.

## systemd unit: RQ worker (templated)

```ini
# /etc/systemd/system/myapp-worker@.service
[Unit]
Description=MyApp Python Worker (%i)
After=network-online.target redis.service
Wants=network-online.target
PartOf=myapp.target

[Service]
Type=exec
User=app
Group=app
WorkingDirectory=/var/www/myapp-sidecar/current
EnvironmentFile=/etc/myapp/worker.env
ExecStart=/var/www/myapp-sidecar/current/.venv/bin/rq worker high default low \
    --url ${REDIS_URL} \
    --name worker-%H-%i \
    --worker-ttl 420 \
    --max-jobs 500
Restart=on-failure
RestartSec=5s
TimeoutStopSec=90

# Same hardening block as sidecar
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/var/app/storage /var/log/myapp
MemoryMax=2G

[Install]
WantedBy=multi-user.target
```

Enable multiple instances: `systemctl enable --now myapp-worker@1 myapp-worker@2`.

## Target file (group services)

```ini
# /etc/systemd/system/myapp.target
[Unit]
Description=MyApp services
Requires=myapp-sidecar.service myapp-worker@1.service myapp-worker@2.service
After=myapp-sidecar.service

[Install]
WantedBy=multi-user.target
```

`systemctl restart myapp.target` restarts the lot in order.

## nginx reverse proxy (internal only)

PHP and Python on the same host: PHP calls `127.0.0.1:8001` directly — no nginx in the path. Simpler and faster.

Different hosts: nginx proxies from the PHP host to the Python host over the internal network.

```nginx
# /etc/nginx/sites-available/myapp-internal-py
upstream myapp_py {
    server 10.0.0.5:8001 max_fails=3 fail_timeout=10s;
    keepalive 16;
}

server {
    listen 127.0.0.1:8011;

    # Only the PHP host may call this
    allow 10.0.0.4;
    deny all;

    access_log /var/log/nginx/myapp-py-access.log main;
    error_log /var/log/nginx/myapp-py-error.log;

    location / {
        proxy_pass http://myapp_py;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Correlation-Id $http_x_correlation_id;

        proxy_connect_timeout 2s;
        proxy_send_timeout    30s;
        proxy_read_timeout    30s;

        proxy_next_upstream error timeout http_502 http_503;
        proxy_next_upstream_tries 2;
    }
}
```

Never put the sidecar behind a public-facing `server` block. Bind to `127.0.0.1` or a private IP only.

## Zero-downtime restart: sidecar (blue/green)

Uvicorn restarts under systemd already drop ~0 requests (graceful shutdown + new process starts). When that is not good enough (long-lived SSE, streaming), use blue/green.

1. Old sidecar listens on `:8001`. New release is installed.
2. Start the new sidecar on `:8002` via `myapp-sidecar-green.service`.
3. Flip nginx upstream or PHP config to `:8002`. Reload nginx/PHP-FPM.
4. Wait `drain_seconds` (e.g. 60) for in-flight requests on `:8001` to finish.
5. Stop `:8001`. Rename green unit to blue for the next cycle.

Simplest implementation: two nearly identical unit files differing only in `--port` and the `PartOf` target. A deploy script toggles between them.

## Zero-downtime restart: workers

Workers cannot accept new work for 0 ms. Protocol:

1. `systemctl reload myapp-worker@1` — sends `SIGUSR1` in RQ; worker finishes current job, exits cleanly.
2. systemd restarts it — the new process starts with the new code.
3. Roll through worker units one at a time so total capacity never drops below N-1.

Celery: use `celery control shutdown` or send `TERM`; configure `TimeoutStopSec` to allow the longest-running task to complete.

## Log rotation

journald captures all stdout/stderr. Configure limits in `/etc/systemd/journald.conf`:

```text
SystemMaxUse=2G
MaxRetentionSec=14day
```

File-based logs (from the log shipper, or structured JSON to a file) rotate via logrotate:

```text
# /etc/logrotate.d/myapp
/var/log/myapp/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    copytruncate
    su app app
}
```

Prefer journald + log shipper (Vector/Promtail) over file rotation. It is less likely to lose lines on rotation.

## Migrations

Run migrations as a one-shot systemd unit *before* the new sidecar version starts, not from the sidecar itself.

```ini
# /etc/systemd/system/myapp-migrate.service
[Unit]
Description=MyApp DB migrations
After=mysql.service

[Service]
Type=oneshot
User=app
Group=app
WorkingDirectory=/var/www/myapp-sidecar/current
EnvironmentFile=/etc/myapp/sidecar.env
ExecStart=/var/www/myapp-sidecar/current/.venv/bin/alembic upgrade head
```

Deploy script order:

1. Install new release.
2. `systemctl start myapp-migrate.service` (blocks until success).
3. `systemctl restart myapp-sidecar.service`.
4. `systemctl reload myapp-worker@*.service`.

Additive migrations only. Destructive ones (DROP, NOT NULL on existing columns) span two releases — add column, deploy code, backfill, switch, then later drop.

## Preflight check

A short Python script that asserts the service can start. Run as `ExecStartPre`.

```python
# src/service_name/preflight.py
import sys
from .settings import settings

def main():
    required = ["internal_secret", "database_url", "redis_url"]
    missing = [k for k in required if not getattr(settings, k, None)]
    if missing:
        print(f"missing settings: {missing}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
```

Catches the 90% of production incidents that come from a missing env variable after a deploy.

## Rollback

```bash
# Flip the symlink, restart
ln -sfn /var/www/myapp-sidecar/releases/$PREVIOUS /var/www/myapp-sidecar/current
systemctl restart myapp-sidecar myapp-worker@*
```

Roll back migrations only if the new ones were non-additive. If they were additive, the old code can safely read the new schema.
