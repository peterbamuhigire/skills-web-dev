---
name: linux-webstack
description: Manage the web stack on Ubuntu/Debian servers — Nginx reverse proxy (config, reload, debug 502), Apache backend (port 8080 vhosts), PHP-FPM (pool tuning, restart), and Node.js API services (systemd). Covers the Nginx+Apache dual-stack pattern where Nginx fronts all traffic and proxies PHP apps to Apache on port 8080.
---
# Web Stack Management

```
Client → Nginx (443/80)
           ├── Astro/static → /dist/ folders
           ├── PHP direct → PHP-FPM socket
           ├── PHP apps → Apache (port 8080)
           └── Node.js APIs → localhost:<port>
```

---

## Nginx

```bash
sudo nginx -t                                      # test config (always first)
sudo nginx -t && sudo systemctl reload nginx       # graceful reload
sudo systemctl restart nginx                       # full restart

# Enable / disable site
sudo ln -s /etc/nginx/sites-available/<domain>.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/<domain>.conf

sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Debug 502 Bad Gateway

```bash
sudo tail -20 /var/log/nginx/error.log           # what upstream is failing?
sudo systemctl status php8.3-fpm                 # PHP-FPM sites
sudo systemctl status apache2                    # Apache-proxied sites
ls -la /run/php/php8.3-fpm.sock                  # FPM socket present?
sudo systemctl restart php8.3-fpm               # fix
```

Config patterns and templates: `references/config-patterns.md`

---

## Apache (Port 8080)

```bash
sudo apache2ctl configtest                        # test config
sudo apache2ctl configtest && sudo systemctl reload apache2
sudo a2ensite <domain>.conf
sudo a2dissite <domain>.conf
sudo tail -f /var/log/apache2/error.log
```

---

## PHP-FPM

```bash
sudo php-fpm8.3 -t                               # test config
sudo systemctl reload php8.3-fpm                # graceful
sudo systemctl restart php8.3-fpm               # full restart
sudo tail -f /var/log/php8.3-fpm.log
```

### Tune Workers

```bash
sudo nano /etc/php/8.3/fpm/pool.d/www.conf
# Key settings:
# pm.max_children = 20  (RAM-dependent: (RAM_MB - 256) / avg_worker_MB)
# pm.start_servers = 4
# pm.min_spare_servers = 2
# pm.max_spare_servers = 8
# pm.max_requests = 500
sudo systemctl reload php8.3-fpm
```

---

## Node.js Services

```bash
sudo systemctl status <service-name>
sudo journalctl -u <service-name> -n 50 --no-pager
sudo systemctl restart <service-name>
```

Create new Node.js systemd unit: see `references/config-patterns.md`

---

## nginx.conf Global Settings

```bash
sudo nano /etc/nginx/nginx.conf
```
```nginx
worker_processes auto;
server_tokens off;         # hide version
client_max_body_size 64M;  # upload limit
gzip on;
```
