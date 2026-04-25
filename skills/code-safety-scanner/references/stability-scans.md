# Stability Scan Patterns (Checks 6-13)

Detailed grep patterns and analysis for Category B: Server Stability / 500 Error Risks.

## Check 6: Unhandled Runtime Exceptions

### PHP

```php
// Scan for unprotected JSON parsing
json_decode($input)          // without try-catch or json_last_error() check
json_decode($input, true, 512, JSON_THROW_ON_ERROR)  // good if in try-catch

// Scan for unprotected file operations
file_get_contents($path)     // without file_exists() or try-catch
fopen($path, 'r')            // without error handling

// Scan for missing global handler
set_exception_handler        // should exist in bootstrap
set_error_handler            // should exist in bootstrap
```

Grep: `json_decode|file_get_contents|fopen|curl_exec|simplexml_load` without nearby `try|catch|json_last_error|file_exists`

### Node.js/JavaScript

```javascript
// Scan for unprotected JSON parsing
JSON.parse(data)             // without try-catch

// Scan for unprotected async operations
await fetch(url)             // without try-catch
await db.query()             // without try-catch

// Scan for missing global handlers
process.on('uncaughtException')      // should exist
process.on('unhandledRejection')     // should exist
```

Grep: `JSON\.parse|await.*fetch|await.*query|await.*find` then check for enclosing `try`

### Python

```python
# Scan for unprotected operations
json.loads(data)             # without try-except
open(path)                   # without try-except or context manager
requests.get(url)            # without try-except or timeout
```

### Null/Undefined Access

```
# JavaScript - optional chaining missing
\.user\.email                # should be ?.user?.email on API responses
\.data\.results\.length      # chain without null checks

# PHP - null access
->property                   # on potentially null objects without ?-> (PHP 8)
```

## Check 7: Misconfigured Environment Variables

### Scan Procedure

1. Find all env var references in code:

```
# PHP
\$_ENV\[|getenv\(|env\(
# Node
process\.env\.|dotenv
# Python
os\.environ|os\.getenv|environ\.get
```

2. Extract variable names from matches.

3. Check `.env.example` or `.env.template` exists and lists all vars.

4. Check for startup validation:

```
# Good patterns - validation at startup
requiredEnvVars|validateEnv|checkEnv|envSchema|envalid|joi.*env|zod.*env
# PHP
if (!getenv('DB_HOST')) throw
# Python
if not os.environ.get('DB_HOST'): raise
```

5. Check for dangerous defaults:

```
# Defaults that mask missing config
\|\|.*localhost|localhost.*fallback
\?\?.*3306|default.*port
getenv.*\?\?|\.get\(.*,.*default
```

## Check 8: Misconfigured File Paths

### Scan Patterns

```
# Hardcoded absolute paths (almost always wrong in production)
/home/|/Users/|C:\\Users\\|/var/www/
/tmp/  # OK for temp files, but check if temp dir is configurable

# Relative paths without resolution
\./uploads/|\.\./config/|\./storage/
# Should use: path.join, __DIR__, os.path.join, path.resolve

# Missing existence checks before file ops
readFileSync|file_get_contents|open\(
# Should have: existsSync, file_exists, os.path.exists nearby

# User-supplied paths (path traversal risk)
req\.(params|body|query).*path|req\.file
\$_(GET|POST|REQUEST).*path|file|dir
request\.(GET|POST|args).*path|file
```

## Check 9: Database Connection Problems

### Connection Pool Analysis

```
# PHP - new connection per request (bad for high traffic)
new PDO\(|new mysqli\(|pg_connect\(
# Should use: persistent connections or connection pooler

# Node - no pooling
mysql\.createConnection   # should be createPool
new Client\(              # pg: should use Pool
mongoose\.connect         # check poolSize option

# Python
psycopg2\.connect         # should use pool
pymysql\.connect          # should use pool or SQLAlchemy pool
```

### Connection Lifecycle

```
# Connections in loops (CRITICAL)
for.*\{[\s\S]*?(createConnection|new PDO|connect\()
while.*\{[\s\S]*?(createConnection|new PDO|connect\()

# Missing close/release
\.connect\(               # check for corresponding .end() / .close() / .release()
pool\.getConnection       # check for connection.release() in finally block
```

### Configuration Checks

```
# Missing connection limits
connectionLimit|pool_size|max_connections|poolSize
# Should be explicitly set, not defaulting

# Missing timeouts
connectTimeout|connectionTimeout|acquireTimeout|idleTimeout
# Should be explicitly set
```

## Check 10: Infinite Loops/Recursion

### Direct Patterns

```
# Unbounded loops
while\s*\(\s*true\s*\)|while\s*\(\s*1\s*\)|for\s*\(\s*;\s*;\s*\)
# Check: does it have break/return with reachable condition?

# Recursion without depth limit
function\s+(\w+).*\{[\s\S]*\1\(     # function calls itself
def\s+(\w+).*:[\s\S]*\1\(           # Python self-call
# Check: is there a base case? Is depth bounded?

# Retry without max attempts
retry|attempt|again
# Check: is there a maxRetries/maxAttempts counter?
```

### Event Loop Patterns

```
# Node.js - setInterval without cleanup
setInterval\(                        # check for corresponding clearInterval
# React - useEffect without cleanup
useEffect.*setInterval               # check return function clears interval

# Event emitter loops
\.on\(.*\).*\.emit\(                 # handler that emits same event
\.addEventListener.*dispatch          # listener that dispatches triggering event
```

## Check 11: Memory Leaks

### Growing Collections

```
# Global arrays that grow
(let|var|const)\s+\w+\s*=\s*\[\]    # top-level arrays
# Check: is data ever removed? Is there a size limit?

# Cache without eviction
cache\[|cache\.set|Map\(\)|new Map
# Check: is there a maxSize, TTL, or LRU eviction?
```

### Unclosed Resources

```
# Streams not piped or closed
createReadStream|createWriteStream   # check for .pipe() or .close()
fs\.open                             # check for fs.close

# Database cursors
\.cursor\(\)|\.stream\(\)           # check for .close() in finally

# Event listeners accumulated
addEventListener|\.on\(              # in loops or repeated calls
# Check: corresponding removeEventListener / .off()
```

### Large Memory Operations

```
# Reading entire files into memory
readFileSync|file_get_contents       # for large files, should use streaming
# Loading all DB rows
SELECT \*.*FROM.*(?!LIMIT|WHERE)     # unbounded queries
findAll\(\)|\.find\(\{.*\}\)        # ORM: missing limit/pagination
```

## Check 12: Concurrency Issues

### Shared Mutable State

```
# Global/module-level mutable state in web servers
(let|var)\s+\w+\s*=                  # module-level in Node.js request handlers
global\s+\$                          # PHP globals (less concern with PHP-FPM)
```

### File Write Conflicts

```
# File writes without locking
file_put_contents|writeFileSync|\.write\(
# Check: is flock/lockfile used? Can concurrent requests write same file?
```

### Non-Atomic Operations

```
# Read-modify-write without transaction
SELECT.*UPDATE                       # separate queries, should be atomic
# Counter increments
\+\+|\+= 1|count = count \+ 1       # in concurrent context
# Should use: atomic DB operations, Redis INCR, mutex
```

## Check 13: Data Race Conditions

### Classic Race Patterns

```
# Check-then-act (TOCTOU)
if.*balance.*>=.*amount[\s\S]*balance.*-=.*amount
# Should be: atomic UPDATE with WHERE balance >= amount

# Read-then-write
SELECT.*balance[\s\S]*UPDATE.*balance
# Should be: SELECT ... FOR UPDATE or atomic UPDATE

# Inventory/stock checks
if.*stock.*>.*0[\s\S]*(stock.*--|UPDATE.*stock)
# Should be: UPDATE stock SET qty = qty - 1 WHERE qty > 0
```

### Async Race Patterns (JavaScript)

```
# Shared variable in async operations
let\s+\w+[\s\S]*await[\s\S]*\w+\s*=
# Multiple awaits modifying same variable without synchronization

# Promise.all modifying shared state
Promise\.all.*[\s\S]*\w+\s*(\+\+|\+=|-=)
```

### Session Race Conditions

```
# PHP session writes in parallel AJAX
session_start\(\)
# Multiple concurrent requests can overwrite session data
# Fix: session_write_close() as early as possible, or use DB sessions

# Express session
req\.session\.\w+\s*=
# Concurrent requests can cause lost updates
```
