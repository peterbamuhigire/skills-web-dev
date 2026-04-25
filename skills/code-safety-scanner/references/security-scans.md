# Security Scan Patterns (Checks 1-5)

Detailed grep patterns and analysis procedures per stack for Category A checks.

## Check 1: Hardcoded API Keys - Grep Patterns

### Universal Patterns (all stacks)

```
# High-confidence key patterns
sk_live_[a-zA-Z0-9]{24,}
sk_test_[a-zA-Z0-9]{24,}
pk_live_[a-zA-Z0-9]{24,}
rk_live_[a-zA-Z0-9]{24,}
AKIA[0-9A-Z]{16}                    # AWS access key
AIza[0-9A-Za-z\-_]{35}              # Google API key
ghp_[a-zA-Z0-9]{36}                 # GitHub PAT
xoxb-[0-9]{11,13}-[a-zA-Z0-9-]*    # Slack bot token
SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}  # SendGrid
```

### Frontend-Specific Scan

Target files: `*.js`, `*.ts`, `*.jsx`, `*.tsx`, `*.vue`, `*.svelte`, `*.html`
Exclude: `node_modules/`, `dist/`, `build/`, `vendor/`

```
# Supabase - service_role key in frontend is CRITICAL
supabase.*service_role
SUPABASE_SERVICE_ROLE

# Firebase - check if rules are open
firebaseConfig
apiKey.*=.*["'][A-Za-z0-9_-]{20,}["']

# Generic secret patterns in frontend
(SECRET|PRIVATE|PASSWORD|CREDENTIAL).*=.*["'][^"']{8,}["']
Authorization.*Bearer.*["'][a-zA-Z0-9._-]{20,}["']
```

### Git History Check

```bash
# Check if .env files were ever committed
git log --all --diff-filter=A -- "*.env" ".env*"
git log --all -p -- "*.env" | head -100
```

### False Positive Handling

- `NEXT_PUBLIC_` prefixed vars are intentionally public (but verify they should be)
- Supabase `anon` key is designed for frontend use (but verify RLS is enabled)
- Firebase `apiKey` is semi-public (but verify security rules)
- Test/example keys in documentation are OK

## Check 2: Inverted Auth Logic - Analysis Patterns

### PHP

```php
// DANGEROUS: inverted check
if (!isset($_SESSION['user_id'])) {
    // grants access here instead of blocking
    include 'admin_panel.php';
}

// DANGEROUS: wrong operator
if ($user->role != 'admin') {
    return $this->adminAction(); // should be ==
}
```

Scan: `auth|middleware|guard|login|session` files, trace every `if` branch.

### Node.js/Express

```javascript
// DANGEROUS: next() in wrong branch
app.use((req, res, next) => {
    if (!req.isAuthenticated()) {
        next(); // should be res.status(401)
    }
});

// DANGEROUS: callback returns inverted
const isAdmin = (req) => !req.user?.role === 'admin'; // always false
```

Scan: All middleware files, `passport` config, `jwt.verify` callbacks.

### Python/Django/Flask

```python
# DANGEROUS: decorator that doesn't actually block
def require_auth(f):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            pass  # should return/abort
        return f(*args, **kwargs)
    return wrapper
```

Scan: Decorators, `login_required` implementations, `before_request` hooks.

## Check 3: Open Admin Endpoints - Route Analysis

### PHP (Laravel/Raw)

```
# Scan route definitions
Route::.*admin|dashboard|manage|bulk
# Check if middleware is attached
->middleware('auth')
->middleware('admin')
->middleware('role:')
```

### Express/Node

```
# Routes with admin-like paths
router\.(get|post|put|delete|patch).*(/admin|/dashboard|/manage|/bulk|/users)
app\.(get|post|put|delete|patch).*(/admin|/dashboard|/manage|/bulk|/users)

# Verify middleware chain includes auth
```

### Python/Django

```
# Check urls.py for admin paths without auth
path.*admin|manage|bulk|dashboard
# Verify @login_required or permission decorators
```

## Check 4: Signup/Login Auth Gaps

### Patterns to Scan

```
# Rate limiting check - look for absence of:
rate_limit|throttle|RateLimit|slowDown|express-rate-limit|django-ratelimit

# Email verification - look for absence of:
verify.*email|email.*verif|confirmation.*token|activate.*account

# Password hashing - CRITICAL if found:
password.*=.*\$_(POST|GET|REQUEST)   # PHP direct storage
password:.*req\.body\.password        # Node direct storage
```

## Check 5: Missing Row-Level Security

### Database Query Analysis

```
# Queries without user/tenant scoping
SELECT.*FROM.*(users|orders|profiles|accounts|transactions)
# Should have: WHERE (user_id|tenant_id|owner_id|created_by) =

# Direct ID usage from request
WHERE id = \$_(GET|POST|REQUEST)     # PHP
WHERE id = .*req\.(params|body|query)  # Node
WHERE id = .*request\.(GET|POST|args)  # Python
```

### Supabase-Specific

```
# Check if RLS is enabled
ALTER TABLE.*ENABLE ROW LEVEL SECURITY
# Check if policies exist
CREATE POLICY
# CRITICAL: service_role bypasses RLS
```

### ORM Analysis

Look for model queries without scope:
- Laravel: `Model::find($id)` without `->where('user_id', auth()->id())`
- Sequelize: `Model.findByPk(id)` without user scope
- Django: `Model.objects.get(pk=id)` without user filter
