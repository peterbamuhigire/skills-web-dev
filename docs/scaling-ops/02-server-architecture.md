# Server Architecture

**Nginx reverse proxy, Docker Compose isolation, VPS specs and providers**

---

## Recommended VPS Providers

### Tier 1 — Primary Recommendation: Hetzner

Hetzner Cloud (hetzner.com/cloud) is the best value for a serious solo studio.

| Server | vCPU | RAM | SSD | Price/month | Use Case |
|--------|------|-----|-----|-------------|----------|
| CX22 | 2 | 4GB | 40GB | €3.79 | Dev/staging |
| CX32 | 4 | 8GB | 80GB | €5.99 | Small app server |
| CX42 | 8 | 16GB | 160GB | €11.09 | Production web server |
| CX52 | 16 | 32GB | 320GB | €19.59 | High-traffic or DB server |
| AX41 | 4 core EPYC | 64GB | 2×512GB NVMe | €43.90 | Dedicated server, Medic8 |

**Hetzner advantages:**
- EU data centres (Finland, Germany, US) — GDPR compliant
- Private networking included free between servers
- Snapshots and backups built in
- Block volumes for extra storage
- Excellent uptime (99.9%+ SLA)

### Tier 2 — Alternative: DigitalOcean / Vultr / Linode

All comparable to Hetzner. Slightly more expensive per-core but often easier
UX and more English-language documentation. Good if you need US East Coast presence.

### Avoid for Production: Shared Hosting

cPanel, Hostinger shared, or similar. No isolation, no Docker, no private networking.
Fine for static sites. Not for SaaS.

---

## Production Server Layout (Step 2 Target)

```
Internet
    │
Cloudflare (WAF + CDN + DDoS)
    │
    ▼
[Web VPS — CX42, €11/month]
    Nginx (reverse proxy, port 80/443)
    Docker containers per product:
    ├── medic8-app:8081
    ├── saas-product-2:8082
    └── saas-product-3:8083
    │
    Private network (10.x.x.x)
    │
    ▼
[DB VPS — CX32, €5.99/month]
    MySQL 8
    Bind to private IP only
    One database per product
    Automated backups to B2
    │
    ▼
[Backblaze B2]
    MySQL dumps (daily)
    User-uploaded files
    Logs archive
```

**Total monthly cost at Step 2:** ~€17–21/month for web + DB
(Compare: AWS equivalent ≈ $150–250/month)

---

## Nginx Reverse Proxy Configuration

Nginx sits at the front of the web VPS and routes traffic to Docker containers.

### Install Nginx

```bash
sudo apt update && sudo apt install -y nginx certbot python3-certbot-nginx
```

### Site Configuration Pattern

```nginx
# /etc/nginx/sites-available/medic8
server {
    listen 80;
    server_name medic8.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name medic8.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/medic8.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/medic8.yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'" always;

    # Proxy to Docker container
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Upload file size limit
        client_max_body_size 50M;

        # Timeouts (increase for AI endpoints)
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/medic8 /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

SSL via Let's Encrypt (when NOT behind Cloudflare):
```bash
sudo certbot --nginx -d medic8.yourdomain.com
```

When behind Cloudflare: use Cloudflare Origin Certificates instead of Let's Encrypt.

---

## Docker Compose Per Product

### Directory Structure

```
/srv/
├── medic8/
│   ├── docker-compose.yml
│   ├── .env                    ← DB password, API keys — never in Git
│   ├── nginx.conf              ← App-level Nginx config (inside container)
│   └── app/                   ← PHP source code
│       └── public/
├── saas-product-2/
│   ├── docker-compose.yml
│   ├── .env
│   └── app/
```

### docker-compose.yml Pattern (PHP/Laravel app)

```yaml
# /srv/medic8/docker-compose.yml
version: "3.9"

services:
  app:
    image: php:8.3-fpm-alpine
    container_name: medic8-app
    restart: unless-stopped
    volumes:
      - ./app:/var/www/html
      - ./storage:/var/www/html/storage
    environment:
      DB_HOST: ${DB_HOST}          # Private IP of DB VPS
      DB_DATABASE: ${DB_DATABASE}
      DB_USERNAME: ${DB_USERNAME}
      DB_PASSWORD: ${DB_PASSWORD}
    networks:
      - medic8-net

  nginx:
    image: nginx:alpine
    container_name: medic8-nginx
    restart: unless-stopped
    ports:
      - "8081:80"               # Nginx reverse proxy maps to this port
    volumes:
      - ./app:/var/www/html
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - app
    networks:
      - medic8-net

networks:
  medic8-net:
    driver: bridge
```

### Deployment Commands

```bash
# First deploy
cd /srv/medic8
docker compose up -d

# Update after new code push
git pull
docker compose up -d --build

# View logs
docker compose logs -f app

# Restart one service
docker compose restart nginx
```

---

## MySQL DB VPS Configuration

### Secure MySQL Installation

```bash
# On DB VPS
sudo apt install -y mysql-server
sudo mysql_secure_installation

# Bind to private IP only — edit /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 10.x.x.x   # Replace with actual private IP

sudo systemctl restart mysql
```

### Per-Product Database User (Least Privilege)

```sql
-- One database + user per product
CREATE DATABASE medic8_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'medic8_user'@'10.x.x.x' IDENTIFIED BY 'strong-password-here';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER
  ON medic8_prod.* TO 'medic8_user'@'10.x.x.x';
FLUSH PRIVILEGES;
```

Never grant `SUPER`, `FILE`, or `GRANT OPTION` to app users.
Never allow connections from `%` (any host) in production.

---

## File Storage: Backblaze B2

Replace local disk storage for uploaded files (photos, PDFs, documents).

**Why B2 over local disk:**
- Local disk fills up and requires VPS resize (downtime)
- B2 scales infinitely at $6/TB/month (vs AWS S3 at $23/TB)
- Files survive server failures
- CDN-compatible: serve via Cloudflare for free egress

**PHP integration:**

```bash
composer require league/flysystem-aws-s3-v3
```

B2 is S3-compatible — the same AWS SDK works:

```php
$client = new Aws\S3\S3Client([
    'version'  => 'latest',
    'region'   => 'us-west-004',
    'endpoint' => 'https://s3.us-west-004.backblazeb2.com',
    'credentials' => [
        'key'    => $_ENV['B2_KEY_ID'],
        'secret' => $_ENV['B2_APP_KEY'],
    ],
]);
```

Cloudflare + B2 = free egress (Cloudflare is a Bandwidth Alliance partner with B2).
Point your CDN subdomain (cdn.yourdomain.com) to your B2 bucket via Cloudflare.
