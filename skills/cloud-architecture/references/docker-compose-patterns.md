# Docker Compose Patterns

Local-parity `docker-compose.yml` templates that mirror production topology. Use these for development, CI integration tests, and for demo environments. They are not a production runtime.

## Full Stack: Node.js + MySQL + Redis + Vector DB

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime
    image: myapp:dev
    restart: unless-stopped
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
      vector:
        condition: service_started
    ports:
      - "3000:3000"
    volumes:
      - ./src:/app/src:ro
    networks: [appnet]
    healthcheck:
      test: ["CMD", "node", "dist/healthcheck.js"]
      interval: 15s
      timeout: 3s
      retries: 5

  db:
    image: mysql:8.4
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: app
      MYSQL_USER: app
      MYSQL_PASSWORD_FILE: /run/secrets/db_password
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
    volumes:
      - db_data:/var/lib/mysql
    networks: [appnet]
    secrets:
      - db_password
      - db_root_password
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h 127.0.0.1 -uroot -p$$(cat /run/secrets/db_root_password) | grep -q 'mysqld is alive'"]
      interval: 10s
      timeout: 5s
      retries: 10

  cache:
    image: redis:7.4-alpine
    restart: unless-stopped
    command: ["redis-server", "--save", "60", "1000", "--appendonly", "yes"]
    volumes:
      - cache_data:/data
    networks: [appnet]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  vector:
    image: qdrant/qdrant:v1.12.0
    restart: unless-stopped
    environment:
      QDRANT__SERVICE__HTTP_PORT: 6333
    volumes:
      - vector_data:/qdrant/storage
    networks: [appnet]

  mail:
    image: axllent/mailpit:latest
    restart: unless-stopped
    ports:
      - "8025:8025"
      - "1025:1025"
    networks: [appnet]

volumes:
  db_data:
  cache_data:
  vector_data:

networks:
  appnet:
    driver: bridge

secrets:
  db_password:
    file: ./secrets/db_password.txt
  db_root_password:
    file: ./secrets/db_root_password.txt
```

## Rules

- Named volumes for every stateful service. Never bind-mount a database into a host path — filesystem drivers differ and will corrupt data over time.
- `depends_on` with `condition: service_healthy` so the application only boots when the DB actually answers.
- `env_file: .env` is committed only as `.env.example`; the real `.env` is gitignored.
- Secrets are files under `./secrets/` (gitignored), loaded via the Compose `secrets:` block — never inlined into the YAML.
- Use `restart: unless-stopped` so a reboot brings the stack back without auto-restarting a crashed app in a loop.
- One network per project (`appnet`) keeps service DNS names predictable.
- Parity with production: if prod runs MySQL 8.4, dev runs MySQL 8.4. Do not mix versions.

## Add-On Services

### Reverse Proxy (Nginx + Certbot)

```yaml
  proxy:
    image: nginx:1.27-alpine
    restart: unless-stopped
    depends_on:
      - app
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ops/nginx/conf.d:/etc/nginx/conf.d:ro
      - ./ops/nginx/certs:/etc/letsencrypt:ro
    networks: [appnet]

  certbot:
    image: certbot/certbot:latest
    entrypoint: /bin/sh -c "trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done"
    volumes:
      - ./ops/nginx/certs:/etc/letsencrypt
```

### Background Worker

```yaml
  worker:
    image: myapp:dev
    command: ["node", "dist/worker.js"]
    restart: unless-stopped
    env_file: .env
    depends_on:
      cache:
        condition: service_healthy
    networks: [appnet]
    deploy:
      replicas: 2
```

## CI Integration

- GitHub Actions can boot this exact stack with `docker compose up -d` and run integration tests against it.
- Use `docker compose down -v` in the teardown step to purge volumes.
- Pin every image tag by semantic version; never use `latest` in CI.

## Differences From Production

Document these explicitly in the README so nobody ships Compose to production by accident:

- No TLS termination at the application (proxy is dev-only).
- No multi-AZ, no replication, no automated backups.
- No secret store — secrets are files on disk.
- No autoscaling, no load balancer, no health gate before traffic.
- Logs go to stdout; production ships them to CloudWatch/Loki/Datadog.
