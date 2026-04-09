# SSL Configuration Reference

## ssl-params.conf (/etc/nginx/snippets/ssl-params.conf)

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;

add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), camera=(), microphone=()" always;
```

Every SSL vhost must include:
```nginx
include snippets/ssl-params.conf;
```

Verify all SSL vhosts include it:
```bash
sudo grep -r "ssl-params" /etc/nginx/sites-enabled/
```

## Check TLS Version Quality

```bash
# Must not accept TLSv1.0 or TLSv1.1:
openssl s_client -connect <domain>:443 -tls1 2>&1 | grep -E "handshake|alert"
openssl s_client -connect <domain>:443 -tls1_1 2>&1 | grep -E "handshake|alert"
# Both should show: handshake failure

# Check what protocols are accepted:
nmap --script ssl-enum-ciphers -p 443 <domain> 2>/dev/null | grep -E "TLS|SSL"
```

## Certificate Key Type (ECDSA vs RSA)

```bash
sudo certbot certificates | grep "Certificate Path"
# Check key type:
openssl x509 -in /etc/letsencrypt/live/<domain>/cert.pem -text -noout | grep "Public Key"
```

Issue ECDSA cert (preferred):
```bash
sudo certbot --nginx -d <domain> --key-type ecdsa --elliptic-curve secp384r1
```

## phpMyAdmin SSL — Restrict + Protect

```apache
# In Apache vhost for phpMyAdmin:
<Directory /usr/share/phpmyadmin>
    AllowOverride All
    Require ip <your-trusted-ip>
    Require ip 127.0.0.1
</Directory>
```
