# Nginx & Apache Config Templates

## Pattern A — Astro Static Site

```nginx
server {
    listen 80;
    server_name <domain>;
    root /var/www[/html]/<folder>/dist;
    index index.html;
    include snippets/security-dotfiles.conf;
    include snippets/static-files.conf;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## Pattern B — PHP App (Nginx → Apache Port 8080)

```nginx
server {
    listen 80;
    server_name <domain>;
    include snippets/security-dotfiles.conf;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / {
        include snippets/proxy-to-apache.conf;
    }
}
```

## Pattern C — Astro + PHP Hybrid

```nginx
server {
    listen 80;
    server_name <domain>;
    root /var/www/html/<folder>/dist;
    include snippets/security-dotfiles.conf;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location /api/ {
        include snippets/proxy-to-apache.conf;
    }
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## Apache Vhost (Pattern B and C — Port 8080)

```apache
<VirtualHost *:8080>
    ServerName <domain>
    DocumentRoot /var/www/html/<folder>[/public]
    <Directory /var/www/html/<folder>[/public]>
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog  ${APACHE_LOG_DIR}/<domain>-error.log
    CustomLog ${APACHE_LOG_DIR}/<domain>-access.log combined
</VirtualHost>
```

## After Certbot Runs (SSL Block Added Automatically)

Certbot adds SSL directives and HTTP→HTTPS redirect to the Nginx config.
Verify `ssl-params.conf` snippet is included in the SSL block:

```nginx
# Inside the ssl server block, add if missing:
include snippets/ssl-params.conf;
```

## Nginx Proxy Snippet (/etc/nginx/snippets/proxy-to-apache.conf)

```nginx
proxy_pass http://127.0.0.1:8080;
proxy_http_version 1.1;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
```

## Security Dotfiles Snippet (/etc/nginx/snippets/security-dotfiles.conf)

```nginx
location ~ /\. { deny all; return 404; }
location ~* \.(env|git|sql|bak|htpasswd|config)$ { deny all; return 404; }
```
