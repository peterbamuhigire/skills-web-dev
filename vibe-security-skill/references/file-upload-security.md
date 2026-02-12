# File Upload Security - Detailed Guide

## Overview

File upload functionality is one of the most exploited features in web applications. Improper validation can lead to remote code execution, XSS, malware distribution, and denial of service.

## Validation Requirements

### 1. File Type Validation

**Check Multiple Indicators:**
```php
function validateFileType($file, $allowedTypes) {
    // Check extension
    $extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    if (!in_array($extension, $allowedTypes)) {
        throw new Exception('Invalid file extension');
    }

    // Check MIME type
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mimeType = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);

    $allowedMimeTypes = [
        'image/jpeg' => 'jpg',
        'image/png' => 'png',
        'image/gif' => 'gif',
        'application/pdf' => 'pdf'
    ];

    if (!isset($allowedMimeTypes[$mimeType])) {
        throw new Exception('Invalid MIME type');
    }

    // Verify extension matches MIME type
    if ($allowedMimeTypes[$mimeType] !== $extension) {
        throw new Exception('Extension/MIME mismatch');
    }

    // Check magic bytes
    $handle = fopen($file['tmp_name'], 'rb');
    $header = fread($handle, 12);
    fclose($handle);

    if (!verifyMagicBytes($header, $extension)) {
        throw new Exception('Invalid file signature');
    }

    return true;
}
```

### 2. Magic Bytes Verification

```php
function verifyMagicBytes($header, $extension) {
    $magicBytes = [
        'jpg' => ["\xFF\xD8\xFF"],
        'png' => ["\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"],
        'gif' => ["\x47\x49\x46\x38\x37\x61", "\x47\x49\x46\x38\x39\x61"],
        'pdf' => ["\x25\x50\x44\x46"],
        'zip' => ["\x50\x4B\x03\x04", "\x50\x4B\x05\x06"],
    ];

    if (!isset($magicBytes[$extension])) {
        return false;
    }

    foreach ($magicBytes[$extension] as $magic) {
        if (strpos($header, $magic) === 0) {
            return true;
        }
    }

    return false;
}
```

### 3. File Size Limits

```php
// config/upload.php
return [
    'max_size' => 5 * 1024 * 1024, // 5MB default
    'max_size_per_type' => [
        'image' => 2 * 1024 * 1024,      // 2MB for images
        'document' => 10 * 1024 * 1024,  // 10MB for documents
        'video' => 50 * 1024 * 1024,     // 50MB for videos
    ]
];

// Validation
if ($file['size'] > config('upload.max_size')) {
    throw new Exception('File too large');
}

// Also set in php.ini
upload_max_filesize = 10M
post_max_size = 12M
```

### 4. Image Content Validation

```php
function validateImage($filePath) {
    // Try to process the image
    $imageInfo = @getimagesize($filePath);

    if ($imageInfo === false) {
        throw new Exception('Invalid image file');
    }

    // Verify dimensions are reasonable
    [$width, $height] = $imageInfo;
    if ($width > 10000 || $height > 10000) {
        throw new Exception('Image dimensions too large');
    }

    // Re-encode to strip potential malicious data
    $image = imagecreatefromstring(file_get_contents($filePath));
    if ($image === false) {
        throw new Exception('Cannot process image');
    }

    // Save cleaned image
    imagejpeg($image, $filePath, 90);
    imagedestroy($image);

    return true;
}
```

## Common Bypasses and Attacks

### Extension Bypass Techniques

| Attack                     | Example                | Prevention                              |
| -------------------------- | ---------------------- | --------------------------------------- |
| Double extension           | `shell.php.jpg`        | Only allow single extension             |
| Null byte                  | `shell.php%00.jpg`     | Sanitize filename, check for null bytes |
| Case manipulation          | `shell.PhP`            | Lowercase extension before checking     |
| Alternative extensions     | `shell.php5`, `.phtml` | Whitelist specific extensions           |
| Appended extension         | `shell.jpg.php`        | Check final extension only              |
| NTFS alternate data stream | `shell.jpg::$DATA`     | Remove special characters               |

### MIME Type Spoofing

```php
// WRONG - Trust Content-Type header
if ($_FILES['upload']['type'] !== 'image/jpeg') {
    die('Invalid type');
}

// CORRECT - Verify with file analysis
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mimeType = finfo_file($finfo, $_FILES['upload']['tmp_name']);
finfo_close($finfo);
```

### Polyglot Files

Files that are valid as multiple types (e.g., both JPEG and JavaScript).

**Prevention:**
```php
// Parse file as expected type and reject if invalid
$image = @imagecreatefromstring(file_get_contents($file));
if ($image === false) {
    throw new Exception('Not a valid image');
}

// Re-encode to strip embedded data
imagejpeg($image, $targetPath, 90);
imagedestroy($image);
```

### SVG with Embedded JavaScript

```xml
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert(document.cookie)</script>
</svg>
```

**Prevention:**
```php
// Option 1: Don't allow SVG uploads
$allowedTypes = ['jpg', 'png', 'gif']; // No svg

// Option 2: Sanitize SVG
function sanitizeSVG($filePath) {
    $svg = file_get_contents($filePath);

    // Remove script tags
    $svg = preg_replace('/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/i', '', $svg);

    // Remove event handlers
    $svg = preg_replace('/\s*on\w+\s*=\s*["\']?[^"\']*["\']?/i', '', $svg);

    // Remove javascript: URLs
    $svg = preg_replace('/javascript:/i', '', $svg);

    file_put_contents($filePath, $svg);
}
```

### XXE via File Upload

Office documents (DOCX, XLSX) are ZIP files containing XML.

**Prevention:**
```php
// Disable external entities before parsing
libxml_disable_entity_loader(true);

// Or reject office documents if not needed
$allowedTypes = ['jpg', 'png', 'pdf']; // No docx, xlsx
```

### ZIP Slip (Path Traversal in Archives)

```php
function extractZip($zipPath, $destDir) {
    $zip = new ZipArchive();
    $zip->open($zipPath);

    for ($i = 0; $i < $zip->numFiles; $i++) {
        $filename = $zip->getNameIndex($i);

        // Check for path traversal
        if (strpos($filename, '..') !== false) {
            throw new SecurityException('Path traversal detected');
        }

        // Ensure destination is within target directory
        $dest = realpath($destDir) . DIRECTORY_SEPARATOR . $filename;
        if (strpos($dest, realpath($destDir)) !== 0) {
            throw new SecurityException('Invalid extraction path');
        }

        $zip->extractTo($destDir, $filename);
    }

    $zip->close();
}
```

### ImageMagick Exploits

ImageMagick has had multiple critical vulnerabilities (ImageTragick).

**Prevention:**
```php
// Use policy.xml to restrict ImageMagick
// /etc/ImageMagick-6/policy.xml
/*
<policymap>
  <policy domain="coder" rights="none" pattern="EPHEMERAL" />
  <policy domain="coder" rights="none" pattern="URL" />
  <policy domain="coder" rights="none" pattern="HTTPS" />
  <policy domain="coder" rights="none" pattern="MVG" />
  <policy domain="coder" rights="none" pattern="MSL" />
</policymap>
*/

// Keep ImageMagick updated
apt update && apt upgrade imagemagick
```

### Filename Injection

```bash
# Malicious filename
; rm -rf / #.jpg
```

**Prevention:**
```php
function sanitizeFilename($filename) {
    // Remove path components
    $filename = basename($filename);

    // Remove special characters
    $filename = preg_replace('/[^a-zA-Z0-9._-]/', '', $filename);

    // Or use random filename
    $extension = pathinfo($filename, PATHINFO_EXTENSION);
    $filename = bin2hex(random_bytes(16)) . '.' . $extension;

    return $filename;
}
```

## Secure Upload Handling

### 1. Rename Files

```php
function storeUpload($file) {
    // Generate random filename
    $extension = pathinfo($file['name'], PATHINFO_EXTENSION);
    $newName = bin2hex(random_bytes(16)) . '.' . $extension;

    // Store in uploads directory
    $path = '/uploads/' . date('Y/m/d') . '/' . $newName;
    move_uploaded_file($file['tmp_name'], storage_path($path));

    return $path;
}
```

### 2. Store Outside Webroot

```php
// Store in directory not accessible via web server
$uploadPath = '/var/uploads/'; // Outside /var/www/html

// Serve via controller with authorization check
Route::get('/files/{id}', function($id) {
    $file = File::findOrFail($id);

    // Check authorization
    if ($file->user_id !== Auth::id()) {
        abort(403);
    }

    return response()->file($file->path);
});
```

### 3. Serve with Correct Headers

```php
function serveUpload($filePath, $originalName) {
    return response()->file($filePath, [
        'Content-Type' => mime_content_type($filePath),
        'Content-Disposition' => 'attachment; filename="' . $originalName . '"',
        'X-Content-Type-Options' => 'nosniff',
        'Cache-Control' => 'no-cache, no-store, must-revalidate',
    ]);
}
```

### 4. Use Separate Domain

```
Main app:     https://myapp.com
User uploads: https://uploads.myapp.com
```

**Benefits:**
- Isolates uploaded content from main app
- Prevents cookie theft if malicious file executes
- Allows stricter CSP on main domain

### 5. Set Restrictive Permissions

```bash
# Upload directory should not be executable
chmod 750 /var/uploads
find /var/uploads -type f -exec chmod 640 {} \;

# Disable script execution in nginx
location /uploads {
    location ~ \.php$ {
        deny all;
    }
}

# Disable script execution in Apache
<Directory "/var/www/html/uploads">
    php_flag engine off
    AddHandler cgi-script .php .pl .py .jsp .asp .sh .cgi
    Options -ExecCGI
</Directory>
```

## Web Server Configuration

### Nginx

```nginx
location /uploads {
    # Disable PHP execution
    location ~ \.php$ {
        deny all;
    }

    # Set correct headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header Content-Disposition "attachment" always;

    # Limit allowed file types
    location ~* \.(jpg|jpeg|png|gif|pdf)$ {
        try_files $uri =404;
    }
}
```

### Apache

```apache
<Directory "/var/www/html/uploads">
    # Disable PHP execution
    php_flag engine off

    # Set correct headers
    Header set X-Content-Type-Options "nosniff"
    Header set Content-Disposition "attachment"

    # Limit allowed file types
    <FilesMatch "^(?!.*\.(jpg|jpeg|png|gif|pdf)$).*$">
        Require all denied
    </FilesMatch>
</Directory>
```

## Malware Scanning

```php
// Use ClamAV for virus scanning
function scanForMalware($filePath) {
    exec("clamscan --no-summary --infected $filePath", $output, $result);

    if ($result !== 0) {
        unlink($filePath);
        throw new SecurityException('Malware detected');
    }
}

// Integrate into upload process
$file = request()->file('upload');
$file->move($uploadPath);
scanForMalware($uploadPath . '/' . $file->getClientOriginalName());
```

## Complete Upload Validation

```php
class SecureFileUpload
{
    private $allowedTypes = ['jpg', 'jpeg', 'png', 'gif', 'pdf'];
    private $maxSize = 5 * 1024 * 1024; // 5MB

    public function validate($file)
    {
        // Check file was uploaded
        if (!isset($file['tmp_name']) || !is_uploaded_file($file['tmp_name'])) {
            throw new Exception('Invalid upload');
        }

        // Check size
        if ($file['size'] > $this->maxSize) {
            throw new Exception('File too large');
        }

        // Validate extension
        $extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        if (!in_array($extension, $this->allowedTypes)) {
            throw new Exception('Invalid file type');
        }

        // Validate MIME type
        $finfo = finfo_open(FILEINFO_MIME_TYPE);
        $mimeType = finfo_file($finfo, $file['tmp_name']);
        finfo_close($finfo);

        // Verify magic bytes
        $handle = fopen($file['tmp_name'], 'rb');
        $header = fread($handle, 12);
        fclose($handle);

        if (!$this->verifyMagicBytes($header, $extension)) {
            throw new Exception('Invalid file signature');
        }

        // For images, verify they can be processed
        if (in_array($extension, ['jpg', 'jpeg', 'png', 'gif'])) {
            $this->validateImage($file['tmp_name']);
        }

        return true;
    }

    public function store($file)
    {
        // Validate first
        $this->validate($file);

        // Generate safe filename
        $extension = pathinfo($file['name'], PATHINFO_EXTENSION);
        $filename = bin2hex(random_bytes(16)) . '.' . $extension;

        // Create directory structure
        $dateDir = date('Y/m/d');
        $uploadDir = '/var/uploads/' . $dateDir;
        if (!is_dir($uploadDir)) {
            mkdir($uploadDir, 0750, true);
        }

        // Move file
        $path = $uploadDir . '/' . $filename;
        move_uploaded_file($file['tmp_name'], $path);

        // Set permissions
        chmod($path, 0640);

        return [
            'path' => $path,
            'filename' => $filename,
            'original_name' => $file['name'],
        ];
    }
}
```

## Summary

File uploads require comprehensive validation:
1. **Validate file type** using extension, MIME type, and magic bytes
2. **Enforce size limits** server-side
3. **Process/re-encode files** to strip embedded content
4. **Rename files** to prevent injection attacks
5. **Store outside webroot** or use separate domain
6. **Serve with restrictive headers**
7. **Disable script execution** in upload directories
8. **Scan for malware** if accepting files from untrusted users
