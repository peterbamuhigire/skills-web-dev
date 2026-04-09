# Provisioning Steps — Full Commands

## 1. System Update & Base Config

```bash
sudo apt update && sudo apt upgrade -y
sudo hostnamectl set-hostname <server-name>
echo "127.0.1.1 <server-name>" | sudo tee -a /etc/hosts
sudo timedatectl set-timezone Africa/Nairobi
timedatectl
sudo locale-gen en_GB.UTF-8 && sudo update-locale LANG=en_GB.UTF-8
```

## 2. Admin User

```bash
sudo adduser administrator
sudo usermod -aG sudo administrator
# If provisioning from root, copy SSH key:
sudo mkdir -p /home/administrator/.ssh
sudo cp /root/.ssh/authorized_keys /home/administrator/.ssh/
sudo chown -R administrator:administrator /home/administrator/.ssh
sudo chmod 700 /home/administrator/.ssh
sudo chmod 600 /home/administrator/.ssh/authorized_keys
# TEST LOGIN IN NEW TERMINAL BEFORE CONTINUING
```

## 3. SSH Hardening

```bash
sudo nano /etc/ssh/sshd_config.d/99-hardening.conf
```
```
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
X11Forwarding no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 3
```
```bash
sudo sshd -t && sudo systemctl restart sshd
# VERIFY LOGIN IN SECOND TERMINAL FIRST
```

## 4. UFW

```bash
sudo ufw default deny incoming && sudo ufw default allow outgoing
sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp
sudo ufw enable && sudo ufw status verbose
```

## 5. Automatic Updates

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades    # select Yes
```

## 6. Web Stack

```bash
# Nginx
sudo apt install -y nginx
sudo systemctl enable nginx

# Apache on port 8080
sudo apt install -y apache2
sudo nano /etc/apache2/ports.conf
# Change: Listen 80 → Listen 8080
sudo nano /etc/apache2/sites-available/000-default.conf
# Change: <VirtualHost *:80> → <VirtualHost *:8080>
sudo systemctl enable apache2 && sudo systemctl restart apache2
ss -tlnp | grep apache   # verify: 0.0.0.0:8080

# PHP 8.3
sudo apt install -y php8.3-fpm php8.3-cli php8.3-mysql php8.3-pgsql \
    php8.3-curl php8.3-mbstring php8.3-xml php8.3-zip php8.3-gd \
    php8.3-redis php8.3-intl php8.3-bcmath
sudo systemctl enable php8.3-fpm
```

## 7. Databases

```bash
# MySQL 8
sudo apt install -y mysql-server
sudo systemctl enable mysql
sudo mysql_secure_installation
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
# Set: bind-address = 127.0.0.1
sudo systemctl restart mysql
ss -tlnp | grep 3306   # must show 127.0.0.1:3306

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable postgresql

# Redis
sudo apt install -y redis-server
sudo systemctl enable redis
sudo nano /etc/redis/redis.conf
# Ensure: bind 127.0.0.1 -::1 | Set: requirepass <strong-password>
sudo systemctl restart redis
ss -tlnp | grep 6379   # must show 127.0.0.1:6379
```

## 8. Supporting Tools

```bash
# Node.js LTS
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# fail2ban
sudo apt install -y fail2ban && sudo systemctl enable fail2ban

# Certbot (nginx + apache plugins)
sudo apt install -y certbot python3-certbot-nginx python3-certbot-apache

# rclone
curl https://rclone.org/install.sh | sudo bash

# msmtp
sudo apt install -y msmtp msmtp-mta
```

## 9. Nginx Snippets & Catch-All

```bash
sudo mkdir -p /etc/nginx/snippets

# security-dotfiles.conf
cat << 'EOF' | sudo tee /etc/nginx/snippets/security-dotfiles.conf
location ~ /\. { deny all; return 404; }
location ~* \.(env|git|sql|bak|htpasswd|config)$ { deny all; return 404; }
EOF

# ssl-params.conf
cat << 'EOF' | sudo tee /etc/nginx/snippets/ssl-params.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
ssl_stapling on;
ssl_stapling_verify on;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
EOF

# proxy-to-apache.conf
cat << 'EOF' | sudo tee /etc/nginx/snippets/proxy-to-apache.conf
proxy_pass http://127.0.0.1:8080;
proxy_http_version 1.1;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
EOF

# Catch-all (rejects unknown hostnames)
cat << 'EOF' | sudo tee /etc/nginx/sites-available/00-default.conf
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    listen 443 ssl default_server;
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    server_name _;
    return 444;
}
EOF

sudo ln -s /etc/nginx/sites-available/00-default.conf /etc/nginx/sites-enabled/
sudo nano /etc/nginx/nginx.conf   # add: server_tokens off;
sudo nginx -t && sudo systemctl reload nginx
```

## 10. Clone Linux Skills & Scripts

```bash
cd /home/administrator
git clone <linux-skills-repo-url> linux-skills

sudo ln -sf /home/administrator/linux-skills/scripts/server-audit.sh \
    /usr/local/bin/check-server-security
sudo chmod +x /usr/local/bin/check-server-security

sudo cp /home/administrator/linux-skills/scripts/update-all-repos \
    /usr/local/bin/update-all-repos
sudo chmod +x /usr/local/bin/update-all-repos
printf '#!/bin/bash\n/usr/local/bin/update-all-repos "$@"\n' | \
    sudo tee /usr/local/bin/update-repos
sudo chmod +x /usr/local/bin/update-repos
```

## 11. Post-Install Security Check

```bash
sudo check-server-security
# Fix all FAIL items before going to production
# Then run: linux-server-hardening
```
