# Server-Side Security - Detailed Guide

## Overview

Server-side vulnerabilities exploit weaknesses in how applications process requests, interact with external systems, and handle data. These attacks can compromise servers, databases, and internal networks.

## SQL Injection

### What is SQL Injection?

SQL injection occurs when user input is incorporated into SQL queries without proper parameterization, allowing attackers to manipulate database queries.

### Attack Examples

**Authentication Bypass:**
```sql
-- Vulnerable query
SELECT * FROM users WHERE username = '$username' AND password = '$password'

-- Attack input
username: admin' --
password: anything

-- Resulting query
SELECT * FROM users WHERE username = 'admin' -- ' AND password = 'anything'
-- The -- comments out the password check
```

**Data Extraction:**
```sql
-- Vulnerable query
SELECT * FROM products WHERE id = $id

-- Attack input
id: 1 UNION SELECT username, password, NULL FROM users --

-- Resulting query
SELECT * FROM products WHERE id = 1 UNION SELECT username, password, NULL FROM users --
```

### Prevention Methods

#### 1. Parameterized Queries (Primary Defense)

**PHP (PDO):**
```php
// WRONG
$query = "SELECT * FROM users WHERE id = " . $_GET['id'];
$result = $pdo->query($query);

// CORRECT
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$_GET['id']]);
$result = $stmt->fetch();
```

**Node.js:**
```javascript
// WRONG
const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
const result = await db.query(query);

// CORRECT
const query = 'SELECT * FROM users WHERE id = ?';
const result = await db.query(query, [req.params.id]);
```

**Python:**
```python
# WRONG
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# CORRECT
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

#### 2. ORM Usage

**Laravel (Eloquent):**
```php
// Safe - uses parameterization
$user = User::where('id', $userId)->first();

// DANGEROUS - raw query without bindings
$user = DB::select("SELECT * FROM users WHERE id = $userId");

// CORRECT - raw query with bindings
$user = DB::select("SELECT * FROM users WHERE id = ?", [$userId]);
```

**Sequelize (Node.js):**
```javascript
// Safe
const user = await User.findOne({ where: { id: userId } });

// DANGEROUS - raw query
const user = await sequelize.query(`SELECT * FROM users WHERE id = ${userId}`);

// CORRECT - raw query with replacements
const user = await sequelize.query(
  'SELECT * FROM users WHERE id = ?',
  { replacements: [userId], type: QueryTypes.SELECT }
);
```

#### 3. Special Cases

**ORDER BY Clause:**
```php
// Can't parameterize column names - must whitelist
$allowedColumns = ['name', 'email', 'created_at'];
$sortColumn = in_array($request->sort, $allowedColumns) ? $request->sort : 'id';

$query = "SELECT * FROM users ORDER BY $sortColumn DESC";
```

**LIKE Patterns:**
```php
// Escape wildcards if user input shouldn't include them
$search = str_replace(['%', '_'], ['\\%', '\\_'], $request->search);
$stmt = $pdo->prepare("SELECT * FROM users WHERE name LIKE ?");
$stmt->execute(["%$search%"]);
```

**IN Clause with Dynamic List:**
```php
// Create placeholders for each item
$ids = [1, 2, 3, 4, 5];
$placeholders = implode(',', array_fill(0, count($ids), '?'));
$stmt = $pdo->prepare("SELECT * FROM users WHERE id IN ($placeholders)");
$stmt->execute($ids);
```

### Testing for SQL Injection

**Manual Test Payloads:**
```
'
"
`
' OR '1'='1
' OR '1'='1' --
' OR '1'='1' /*
admin' --
admin' #
' UNION SELECT NULL--
' AND 1=0 UNION ALL SELECT 'admin', '81dc9bdb52d04dc20036dbd8313ed055'
1' AND EXTRACTVALUE(1, CONCAT(0x5c, (SELECT database())))--
```

---

## Server-Side Request Forgery (SSRF)

### What is SSRF?

SSRF occurs when an application makes HTTP requests to URLs controlled or influenced by users, allowing attackers to scan internal networks, access cloud metadata, or bypass access controls.

### Vulnerable Features

- Webhooks (user provides callback URL)
- URL preview/unfurling
- PDF generation from URLs
- Image fetching from URLs
- RSS/feed readers
- API integrations with user-provided endpoints
- Proxy functionality
- HTML-to-image/PDF converters

### Attack Examples

**Cloud Metadata Access:**
```bash
# AWS metadata endpoint
http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Returns AWS credentials
{
  "AccessKeyId": "ASIA...",
  "SecretAccessKey": "...",
  "Token": "..."
}
```

**Internal Network Scanning:**
```bash
# Scan internal network
for i in {1..255}; do
  curl "https://target.com/preview?url=http://192.168.1.$i/"
done
```

### Prevention Strategies

#### 1. Allowlist Approach (Preferred)

```php
// Only allow specific domains
$allowedDomains = [
    'api.stripe.com',
    'api.github.com',
    'webhook.example.com'
];

$parsedUrl = parse_url($userUrl);
if (!in_array($parsedUrl['host'], $allowedDomains)) {
    throw new SecurityException('Domain not allowed');
}
```

#### 2. DNS Resolution and Validation

```php
function isSafeUrl($url) {
    $parsed = parse_url($url);

    // Only allow HTTP/HTTPS
    if (!in_array($parsed['scheme'], ['http', 'https'])) {
        return false;
    }

    // Resolve DNS
    $ip = gethostbyname($parsed['host']);

    // Block private IP ranges
    if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) === false) {
        return false;
    }

    // Block cloud metadata IPs
    $blockedIPs = ['169.254.169.254', '::ffff:169.254.169.254'];
    if (in_array($ip, $blockedIPs)) {
        return false;
    }

    return true;
}
```

#### 3. Network Segmentation

```yaml
# docker-compose.yml
services:
  app:
    networks:
      - public
      - internal

  url-fetcher:
    networks:
      - public  # Can access internet
      # NOT connected to internal network

  database:
    networks:
      - internal  # Only accessible internally
```

### IP Bypass Techniques to Block

**Decimal IP:**
```
http://2130706433  # 127.0.0.1 in decimal
```

**Octal IP:**
```
http://0177.0.0.1  # 127.0.0.1 in octal
```

**Hexadecimal IP:**
```
http://0x7f.0x0.0x0.0x1  # 127.0.0.1 in hex
```

**IPv6 Localhost:**
```
http://[::1]
http://[::ffff:127.0.0.1]  # IPv4-mapped IPv6
```

**Short Notation:**
```
http://127.1  # Expands to 127.0.0.1
http://localhost
```

### DNS Rebinding Prevention

```php
// Resolve DNS and validate
$hostname = parse_url($url)['host'];
$ip1 = gethostbyname($hostname);

// Validate IP is not internal
if (!isSafeIP($ip1)) {
    throw new SecurityException('Internal IP blocked');
}

// Wait a moment
sleep(1);

// Resolve again and ensure it hasn't changed
$ip2 = gethostbyname($hostname);
if ($ip1 !== $ip2) {
    throw new SecurityException('DNS rebinding detected');
}

// Make request using the validated IP
// Pin the IP to prevent re-resolution
$context = stream_context_create([
    'http' => [
        'header' => "Host: $hostname\r\n"
    ]
]);
$response = file_get_contents("http://$ip1/", false, $context);
```

---

## XML External Entity (XXE)

### What is XXE?

XXE vulnerabilities occur when XML parsers process external entity references in user-supplied XML, allowing file disclosure, SSRF, and denial of service.

### Attack Example

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>
  <data>&xxe;</data>
</root>
```

### Vulnerable Scenarios

- SOAP APIs
- XML file uploads
- SVG file processing
- Office document parsing (DOCX, XLSX, PPTX)
- SAML authentication
- RSS/Atom feed processing
- Configuration file parsing

### Prevention by Language

**PHP:**
```php
// Disable external entities
libxml_disable_entity_loader(true);

// Use XMLReader with safe settings
$reader = new XMLReader();
$reader->setParserProperty(XMLReader::SUBST_ENTITIES, false);
$reader->XML($xml);
```

**Python (lxml):**
```python
from lxml import etree

# Safe parser
parser = etree.XMLParser(resolve_entities=False, no_network=True)
tree = etree.fromstring(xml_data, parser)

# Or use defusedxml
from defusedxml import ElementTree
tree = ElementTree.fromstring(xml_data)
```

**Java:**
```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();

// Disable external entities
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbf.setExpandEntityReferences(false);

DocumentBuilder db = dbf.newDocumentBuilder();
Document doc = db.parse(new InputSource(new StringReader(xml)));
```

**Node.js:**
```javascript
// Use libraries that disable DTD processing by default
const { parseString } = require('xml2js');

// libxmljs with safe settings
const libxmljs = require('libxmljs');
const doc = libxmljs.parseXml(xml, {
  noent: false,   // Don't substitute entities
  dtdload: false, // Don't load DTD
  dtdvalid: false // Don't validate against DTD
});
```

**.NET:**
```csharp
XmlReaderSettings settings = new XmlReaderSettings();
settings.DtdProcessing = DtdProcessing.Prohibit;
settings.XmlResolver = null;

using (XmlReader reader = XmlReader.Create(stream, settings))
{
    // Parse XML
}
```

---

## Path Traversal

### What is Path Traversal?

Path traversal (directory traversal) occurs when user input controls file paths, allowing access to files outside intended directories.

### Attack Examples

**Basic Traversal:**
```
../../etc/passwd
../../../../windows/system32/config/sam
```

**URL Encoding:**
```
..%2F..%2F..%2Fetc%2Fpasswd
```

**Double Encoding:**
```
..%252F..%252F..%252Fetc%252Fpasswd
```

**Null Byte:**
```
../../etc/passwd%00.png
```

### Prevention Strategies

#### 1. Indirect References

```php
// Don't use user input directly in paths
$files = [
    'invoice' => '/uploads/invoices/2024-001.pdf',
    'receipt' => '/uploads/receipts/2024-001.pdf'
];

$fileKey = $request->input('file');
$filePath = $files[$fileKey] ?? null;

if (!$filePath) {
    abort(404);
}

return response()->file($filePath);
```

#### 2. Canonicalization and Validation

```php
function safeJoin($baseDirectory, $userPath) {
    // Ensure base is absolute and normalized
    $base = realpath($baseDirectory);

    if ($base === false) {
        throw new Exception('Invalid base directory');
    }

    // Join user path to base
    $full = realpath($base . DIRECTORY_SEPARATOR . $userPath);

    // Ensure result is still within base directory
    if ($full === false || strpos($full, $base) !== 0) {
        throw new SecurityException('Path traversal detected');
    }

    return $full;
}

// Usage
$safe = safeJoin('/var/www/uploads', $request->input('file'));
```

#### 3. Input Sanitization

```php
// Remove dangerous characters
$filename = preg_replace('/[^a-zA-Z0-9_.-]/', '', $request->input('file'));

// Ensure no traversal sequences
if (strpos($filename, '..') !== false) {
    throw new SecurityException('Invalid filename');
}

// Validate extension
$allowedExtensions = ['pdf', 'jpg', 'png'];
$extension = pathinfo($filename, PATHINFO_EXTENSION);
if (!in_array(strtolower($extension), $allowedExtensions)) {
    throw new SecurityException('Invalid file type');
}

$path = '/uploads/' . $filename;
```

### Testing for Path Traversal

```bash
# Basic traversal
curl "https://target.com/download?file=../../etc/passwd"

# URL encoded
curl "https://target.com/download?file=..%2F..%2Fetc%2Fpasswd"

# Absolute path
curl "https://target.com/download?file=/etc/passwd"

# Null byte
curl "https://target.com/download?file=../../etc/passwd%00.png"
```

---

## Command Injection

### What is Command Injection?

Command injection occurs when user input is incorporated into system commands, allowing attackers to execute arbitrary commands on the server.

### Attack Examples

```bash
# Vulnerable code
system("ping -c 4 " . $_GET['host']);

# Attack input
host: google.com; cat /etc/passwd

# Resulting command
ping -c 4 google.com; cat /etc/passwd
```

### Prevention

#### 1. Avoid System Commands

```php
// WRONG - Using system command
system("ping -c 4 " . $host);

// CORRECT - Use library
$socket = @fsockopen($host, 80, $errno, $errstr, 5);
if ($socket) {
    echo "Host is up";
    fclose($socket);
} else {
    echo "Host is down";
}
```

#### 2. Escape Arguments

```php
// If you must use system commands
$host = escapeshellarg($_GET['host']);
$output = shell_exec("ping -c 4 $host");
```

#### 3. Whitelist Validation

```php
// Only allow specific values
$allowedCommands = ['status', 'restart', 'stop'];
$command = $_GET['action'];

if (!in_array($command, $allowedCommands)) {
    die('Invalid command');
}

exec("systemctl $command myservice");
```

---

## Insecure Deserialization

### What is Insecure Deserialization?

Deserializing untrusted data can lead to remote code execution, object injection, and other attacks.

### Prevention

**PHP:**
```php
// WRONG - Deserializing user input
$data = unserialize($_POST['data']);

// CORRECT - Use JSON
$data = json_decode($_POST['data'], true);
if ($data === null) {
    throw new Exception('Invalid data');
}
```

**Node.js:**
```javascript
// WRONG
const data = eval(userInput);

// CORRECT
const data = JSON.parse(userInput);
```

**Python:**
```python
# WRONG
import pickle
data = pickle.loads(user_input)

# CORRECT
import json
data = json.loads(user_input)
```

---

## Summary

Server-side vulnerabilities require careful input handling:
1. **Use parameterized queries** for all database interactions
2. **Validate and restrict URLs** in SSRF-prone features
3. **Disable external entities** in XML parsers
4. **Canonicalize and validate paths** for file operations
5. **Avoid system commands** or use proper escaping
6. **Use JSON** instead of native serialization formats
