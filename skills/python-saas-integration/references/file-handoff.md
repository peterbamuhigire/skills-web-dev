# File Handoff

Python generates files (Excel, PDF, CSV, images). PHP delivers them to the user. This file covers temp layout, S3 patterns, local-disk + nginx `X-Accel-Redirect`, and cleanup.

## Principles

1. Files are always namespaced by `tenant_id`. Never a flat bucket/directory.
2. PHP is the authorization boundary. The storage URL is unguessable, short-lived, and never enough on its own.
3. Filenames are opaque — `ulid.ext`. Never user-supplied strings. Never tenant data in the filename.
4. Every generated file has a TTL. Nothing lives forever on temp storage.

## Temp storage layout

```text
/var/app/storage/
|-- tmp/                                 # scratch during generation (atomic move)
|-- tenants/
|   |-- t_01HF8X2N.../
|   |   |-- reports/
|   |   |   |-- 01HF93...-sales-q1.xlsx
|   |   |   `-- 01HF94...-receipts.pdf
|   |   `-- uploads/                     # inbound from user
|   `-- t_01HF8X3A.../
`-- _quarantine/                          # failed AV / poison files
```

Permissions:

- Owner `app`, group `www-data` (or `nginx`), mode `0640` on files, `0750` on directories.
- PHP runs as `www-data`; it reads via group membership. It must not write into `tenants/*/reports/` — only Python does.

Atomic write protocol:

```python
from pathlib import Path
import os, tempfile

def atomic_write(final_path: Path, data: bytes) -> None:
    final_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=Path("/var/app/storage/tmp"),
        suffix=final_path.suffix,
    )
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o640)
        os.replace(tmp, final_path)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise
```

`os.replace` is atomic on the same filesystem. Keep `tmp/` on the same mount as `tenants/`.

## S3 upload (preferred for multi-host)

Use the async S3 client only if your worker is already async. For sync workers, plain `boto3` is fine — Python workers process one job at a time.

```python
# src/service_name/storage/s3.py
import boto3, ulid
from botocore.config import Config
from ..settings import settings

_s3 = boto3.client(
    "s3",
    region_name=settings.s3_region,
    config=Config(
        retries={"max_attempts": 3, "mode": "adaptive"},
        connect_timeout=5,
        read_timeout=30,
    ),
)

def upload_report(tenant_id: str, data: bytes, ext: str, content_type: str) -> str:
    key = f"tenants/{tenant_id}/reports/{ulid.new()}.{ext}"
    _s3.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=data,
        ContentType=content_type,
        ServerSideEncryption="AES256",
        Metadata={"tenant_id": tenant_id},
        CacheControl="private, no-store",
    )
    return key
```

Key rules:

- `ServerSideEncryption="AES256"` or `aws:kms` if compliance requires customer-managed keys.
- Do *not* set `ACL=public-read`. The bucket is private; access is only via signed URLs.
- Set `Metadata.tenant_id` — bucket policy can deny cross-tenant access at IAM layer as defence in depth.

### Signed URLs

Python returns the key; PHP requests a signed URL at download time. This keeps the signing secret in PHP and gives PHP a moment to authorize.

```python
# src/service_name/api/v1/downloads.py  (if PHP calls the sidecar for URLs)
def sign_download(key: str, tenant_id: str, expires: int = 300) -> str:
    # Defensive: refuse to sign a key that is not under this tenant's prefix.
    if not key.startswith(f"tenants/{tenant_id}/"):
        raise AppError("FORBIDDEN_TENANT", "key outside tenant scope", 403)
    return _s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=expires,  # 5 minutes
    )
```

TTL policy:

- Reports downloaded from a clicked link: 300 seconds.
- Long-running batch downloads where user may resume: 3600 seconds max.
- Never > 7 days. Short TTLs contain damage when a URL leaks into logs or analytics.

### PHP side

PHP can also sign directly using the AWS SDK for PHP — usually simpler if S3 is already in PHP's domain. In that case Python only returns the key.

```php
$cmd = $s3->getCommand('GetObject', [
    'Bucket' => $bucket,
    'Key' => $key,
]);
$signed = (string) $s3->createPresignedRequest($cmd, '+5 minutes')->getUri();
```

## Local storage with nginx X-Accel-Redirect

For single-host deployments, local disk + `X-Accel-Redirect` is faster, cheaper, and keeps PHP as the authorization gate.

### nginx config

```nginx
# nginx sites-available/myapp
server {
    # ... usual TLS + PHP-FPM config ...

    # Public route - PHP authorizes, sets X-Accel-Redirect
    location /download/ {
        include fastcgi_params;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
        fastcgi_param SCRIPT_FILENAME /var/www/myapp/public/download.php;
    }

    # Internal route - only accessible via X-Accel-Redirect
    location /_protected_files/ {
        internal;
        alias /var/app/storage/tenants/;
        add_header Content-Disposition $upstream_http_content_disposition;
        add_header Cache-Control "private, no-store";
    }
}
```

### PHP side

```php
<?php
// /var/www/myapp/public/download.php
$fileId = $_GET['id'];
$record = $reportRepo->findForUser($fileId, current_user());  // authorization
if (!$record) { http_response_code(404); exit; }

$relativePath = $record['tenant_id'] . '/reports/' . $record['filename'];
$safeName = 'sales-report-' . $record['date'] . '.xlsx';

header('X-Accel-Redirect: /_protected_files/' . $relativePath);
header('Content-Type: ' . $record['mime']);
header('Content-Disposition: attachment; filename="' . $safeName . '"');
exit;
```

How it works: PHP authorizes, then sets `X-Accel-Redirect`. nginx intercepts, serves the file from `/_protected_files/` (which is `internal` so the user cannot reach it directly). PHP does not stream bytes — nginx does. PHP-FPM memory stays small.

### Sanity checks in PHP

- Reject `..` or absolute paths in `$relativePath`. Build the path from DB fields only.
- `$record['tenant_id']` must match the authenticated user's tenant. Enforce in the query, not in PHP code.
- `filename` from DB must match `^[A-Z0-9_.-]+$` before concatenation.

## Cleanup

Nothing cleans itself up. Schedule it.

### Cron sweep (local disk)

```bash
# /etc/cron.d/myapp-file-sweep
# Every hour, delete files under tenants/*/reports/ older than 72h
17 * * * * app find /var/app/storage/tenants/*/reports/ -type f -mmin +4320 -delete
23 * * * * app find /var/app/storage/tmp/ -type f -mmin +60 -delete
```

Cron runs as the `app` user so permissions are respected. Use `-mmin` not `-mtime` for precision.

### S3 lifecycle rule

```json
{
  "Rules": [{
    "ID": "expire-reports-72h",
    "Status": "Enabled",
    "Filter": { "Prefix": "tenants/" },
    "Expiration": { "Days": 3 }
  }, {
    "ID": "expire-tmp-1d",
    "Status": "Enabled",
    "Filter": { "Prefix": "tmp/" },
    "Expiration": { "Days": 1 }
  }]
}
```

Lifecycle rules cost nothing and never forget. Always prefer them over a cron job for S3.

### Retention overrides

Some files must outlive the default TTL (audit exports, invoices under retention law). Move them out of the temp tree into a dedicated `archive/` prefix with its own (longer) lifecycle policy. Never bump TTLs inside `reports/` — it is a scratch area.

## Virus / content scanning

For user uploads, scan before making the file visible:

1. User uploads to `tenants/{id}/uploads/_incoming/`.
2. Worker runs ClamAV (`clamdscan`) or equivalent.
3. Clean: atomic move to `uploads/`.
4. Infected: move to `_quarantine/`, alert, notify user.

Never skip the scan step because "our users are trusted." Any file that leaves the tenant boundary (to another user, to a print service, into a report) must have been scanned.

## Anti-patterns

- Tenant ID as a query parameter instead of in the path. Too easy to forget the validation.
- Storing the pre-signed URL in the database. It expires; store the key, generate on demand.
- Serving private files through PHP by reading and echoing bytes. Burns PHP-FPM workers. Use `X-Accel-Redirect`.
- "I'll add cleanup later." No you will not. Set the lifecycle rule on day one.
