# Delivery and Downloads

Getting the generated file from the Python service to a user on web, Android, or iOS. Focused on MIME handling, content disposition, signed URLs, filenames, and mobile handoff.

## MIME types

```python
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MIME_XLSM = "application/vnd.ms-excel.sheet.macroEnabled.12"
MIME_XLS  = "application/vnd.ms-excel"
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_DOC  = "application/msword"
MIME_PDF  = "application/pdf"
MIME_CSV  = "text/csv; charset=utf-8"

EXT_MIME = {
    ".xlsx": MIME_XLSX, ".xlsm": MIME_XLSM, ".xls": MIME_XLS,
    ".docx": MIME_DOCX, ".doc": MIME_DOC,
    ".pdf":  MIME_PDF,  ".csv": MIME_CSV,
}
```

Do not use generic `application/octet-stream` when the real type is known — iOS Safari and Android Chrome use the MIME to choose the previewer.

## Content-Disposition with UTF-8 filenames (RFC 5987)

Tenant names contain characters beyond ASCII (é, ñ, 中, ᗊ). Use RFC 5987 `filename*` with URL-encoded UTF-8, alongside an ASCII fallback.

```python
from urllib.parse import quote

def content_disposition(filename: str, *, inline: bool = False) -> str:
    ascii_fallback = filename.encode("ascii", "ignore").decode() or "download"
    quoted = quote(filename, safe="")
    disposition = "inline" if inline else "attachment"
    return f"{disposition}; filename=\"{ascii_fallback}\"; filename*=UTF-8''{quoted}"
```

Example response:

```
Content-Type: application/pdf
Content-Disposition: attachment; filename="acme_sales_jan_2026.pdf"; filename*=UTF-8''acme%20caf%C3%A9_sales_jan_2026.pdf
Cache-Control: private, no-store
X-Content-Type-Options: nosniff
```

`X-Content-Type-Options: nosniff` prevents browsers from overriding the declared type. `Cache-Control: private, no-store` avoids shared-cache leaks of tenant data.

## FastAPI FileResponse

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from pathlib import Path

@app.get("/reports/{job_id}/download")
async def download_report(job_id: str, user = Depends(current_user)):
    job = Job.get_or_404(job_id, tenant_id=user.tenant_id)
    if job.status != "completed":
        return Response(status_code=409, content="Report not ready")
    path: Path = job.artefact_path
    if not path.exists():
        return Response(status_code=410, content="Artefact expired")

    return FileResponse(
        path=str(path),
        media_type=EXT_MIME[path.suffix.lower()],
        headers={
            "Content-Disposition": content_disposition(job.filename),
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
```

`FileResponse` streams from disk; the worker process does not have to hold the full bytes in memory.

## Signed URLs

Prefer signed URLs over direct downloads for three reasons: offload bytes from the app server, time-bounded access, and mobile clients can resume large downloads.

### S3 presigned URL

```python
import boto3
from datetime import timedelta

def s3_signed_url(bucket: str, key: str, filename: str, ttl: timedelta = timedelta(minutes=15)) -> str:
    s3 = boto3.client("s3", region_name=AWS_REGION)
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": bucket,
            "Key": key,
            "ResponseContentType": EXT_MIME[Path(key).suffix.lower()],
            "ResponseContentDisposition": content_disposition(filename),
            "ResponseCacheControl": "private, no-store",
        },
        ExpiresIn=int(ttl.total_seconds()),
    )
```

S3 honours `ResponseContentType` and `ResponseContentDisposition` when you sign them into the URL.

### Custom signed URL (self-hosted)

For self-hosted storage, sign a short-lived HMAC token:

```python
import hmac, hashlib, time, base64

def sign_download(artefact_id: str, filename: str, ttl_seconds: int = 900) -> str:
    expires = int(time.time()) + ttl_seconds
    msg = f"{artefact_id}|{filename}|{expires}".encode()
    sig = base64.urlsafe_b64encode(
        hmac.new(SIGNING_SECRET, msg, hashlib.sha256).digest()
    ).decode().rstrip("=")
    return f"https://api.example.com/d/{artefact_id}?f={quote(filename)}&e={expires}&s={sig}"

def verify_download(artefact_id: str, filename: str, expires: int, sig: str) -> bool:
    if expires < int(time.time()):
        return False
    msg = f"{artefact_id}|{filename}|{expires}".encode()
    expected = base64.urlsafe_b64encode(
        hmac.new(SIGNING_SECRET, msg, hashlib.sha256).digest()
    ).decode().rstrip("=")
    return hmac.compare_digest(expected, sig)
```

Always `hmac.compare_digest` for verification — constant-time.

## TTL policy

```text
Ad-hoc user download        15 minutes    single-use
Emailed report link         24 hours      multi-use, but logged
Scheduled / automation      7 days        referenced by job run id
Audit exports               30 days       compliance retention window
Regulator submission        per regulator usually 7 years — archive tier
```

Store the expiration timestamp on the job record. Background sweeper deletes the artefact and revokes any DB-tracked signed tokens. Never rely only on S3 lifecycle rules — add application-level enforcement so you can revoke early.

## Filename convention

```text
<tenant-slug>_<report-type>_<period>_<timestamp>.<ext>

acme-ltd_sales-dashboard_2026-01_20260415T142200Z.xlsx
kilimanjaro-co_audit-trail_q4-2025_20260415T142200Z.pdf
greenfields-saas_monthly-statement_2026-01_20260415T142200Z.docx
```

- `tenant-slug` — lowercase, hyphenated, ASCII only (derived from tenant id).
- `report-type` — lowercase-hyphen.
- `period` — `YYYY-MM`, `YYYY-Qn`, `YYYY` — pick one per report type; stay consistent.
- `timestamp` — UTC compact ISO 8601 (`YYYYMMDDTHHMMSSZ`). Users will sort by this.
- `ext` — single dot, lowercase.

```python
from slugify import slugify   # python-slugify
from datetime import datetime, UTC

def build_filename(tenant_slug: str, report_type: str, period: str, ext: str) -> str:
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    parts = [slugify(tenant_slug), slugify(report_type), slugify(period), ts]
    return "_".join(parts) + ext
```

## Sanitization

Never use user-supplied strings in filenames or storage keys without sanitising.

```python
import re
from pathlib import PurePosixPath

SAFE_SEGMENT = re.compile(r"[^a-zA-Z0-9._-]")

def safe_segment(s: str, *, max_len: int = 80) -> str:
    cleaned = SAFE_SEGMENT.sub("-", s).strip("-._")
    return cleaned[:max_len] or "x"

def build_storage_key(tenant_id: int, job_id: str, filename: str) -> str:
    # Forbid traversal. Storage keys use POSIX separators regardless of host OS.
    segments = ["tenants", str(tenant_id), "reports", safe_segment(job_id), safe_segment(filename)]
    key = "/".join(segments)
    PurePosixPath(key)  # will raise on suspicious input
    return key
```

Rejected inputs to never accept: `../`, absolute paths, null bytes, control characters. Log and alert when seen.

## Mobile handoff

### iOS

- `URLSession.shared.dataTask` or `downloadTask` with the signed URL. Both work.
- For in-app preview, use `QLPreviewController` (Quick Look). Supports PDF natively. Excel and Word preview work if the file is present; handoff to Files app for edit.
- Universal Link or `UIDocumentInteractionController` offers "Open in..." to hand to Numbers, Pages, or third-party apps.
- `Content-Disposition: inline` + `Content-Type: application/pdf` lets Safari/WKWebView display the PDF directly. Use `attachment` when you want a Save to Files dialog.

### Android

- Prefer `DownloadManager` for large files — resumable, survives app restart, notifies on completion.

```kotlin
val request = DownloadManager.Request(Uri.parse(signedUrl))
    .setTitle(filename)
    .setMimeType(mime)
    .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
    .setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, filename)
    .addRequestHeader("User-Agent", userAgent)   // if the signed URL enforces it
(context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager).enqueue(request)
```

- For in-app PDF preview, use `PdfRenderer` or AndroidX `Pdf` library. Excel and Word require a third-party app.
- Use `FileProvider` if you ever share a bundled file via `Intent.ACTION_SEND`.

### Web

- Give the server-signed URL directly to `<a href={url} download>`. Modern browsers honour the server's `Content-Disposition`.
- For in-page download with progress, use `fetch` + `ReadableStream` + `Blob` + `URL.createObjectURL`. Required for very large files where the browser progress bar is insufficient.

## CORS

If the signed URL is on a different origin from the web app:

```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET
Access-Control-Expose-Headers: Content-Disposition
```

Without `Expose-Headers: Content-Disposition`, JavaScript cannot read the filename from the response.

## Audit trail

Every download event is a security-relevant event. Log:

- job id, user id, tenant id, IP, user-agent
- signed URL token id (not the token itself)
- filename and artefact storage key
- success or failure status, bytes delivered

Retention: align with your general audit log policy — 1 year typical, 7 years for regulated industries.

## Anti-patterns

- Using `application/octet-stream` everywhere — breaks iOS/Android preview.
- Returning a tenant-supplied filename unsanitised — directory traversal, header injection via CRLF.
- Long-lived signed URLs (> 24h) shared in emails — credential-equivalent, easy to leak.
- Relying on client-side filename only (`<a download="...">`) — a user changing the attribute bypasses your naming convention. The server sets it via `Content-Disposition`.
- Forgetting `Cache-Control: private, no-store` — proxies cache tenant artefacts.
- Forgetting `X-Content-Type-Options: nosniff` — IE and some mobile browsers guess MIME and can render `.xlsx` as HTML.
- Not logging download events — incident response has no trail.
