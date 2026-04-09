# Web Stack Config Patterns

## PHP-FPM Direct (fastcgi-php.conf snippet)

```nginx
# /etc/nginx/snippets/fastcgi-php.conf
fastcgi_pass unix:/run/php/php8.3-fpm.sock;
fastcgi_index index.php;
fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
include fastcgi_params;
```

Usage in a vhost:
```nginx
location ~ \.php$ {
    include snippets/fastcgi-php.conf;
}
```

## Nginx Upstream + Node.js Proxy

```nginx
upstream myapp_api {
    server 127.0.0.1:3001;
    keepalive 32;
}

server {
    ...
    location /api/ {
        proxy_pass http://myapp_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Node.js Systemd Unit Template

```ini
# /etc/systemd/system/<service-name>.service
[Unit]
Description=<App Name> API
After=network.target

[Service]
Type=simple
User=administrator
WorkingDirectory=/var/www/html/<folder>
ExecStart=/usr/bin/node <entry>.js
Restart=on-failure
RestartSec=5
Environment=NODE_ENV=production
Environment=PORT=3001

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable <service-name>
sudo systemctl start <service-name>
```

## static-files.conf Snippet

```nginx
# /etc/nginx/snippets/static-files.conf
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    try_files $uri =404;
}
```

## Catch-All (00-default.conf) — Reject Unknown Hostnames

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    server_name _;
    return 444;
}
```

## PHP-FPM Pool Tuning Reference

```ini
; Dynamic mode (recommended for web servers)
pm = dynamic
pm.max_children = 20        ; cap: (available_RAM_MB) / avg_worker_MB
pm.start_servers = 4
pm.min_spare_servers = 2
pm.max_spare_servers = 8
pm.max_requests = 500       ; recycle after N requests (prevents memory leaks)
pm.process_idle_timeout = 10s
```

Typical PHP worker memory by framework:
- Plain PHP: 20-40MB
- Laravel: 50-100MB
- WordPress: 40-80MB
