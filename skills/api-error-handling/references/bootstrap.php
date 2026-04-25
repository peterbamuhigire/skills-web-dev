<?php

/**
 * API Bootstrap
 *
 * Include at the top of all API endpoints.
 * Sets up error handling, CORS, and helper functions.
 */

// Error reporting
error_reporting(E_ALL);
ini_set('display_errors', '0'); // Never display errors in API responses

// Timezone
date_default_timezone_set('UTC');

// Autoload (adjust path to your autoloader)
require_once __DIR__ . '/../vendor/autoload.php';

use App\Http\{ApiResponse, ExceptionHandler};
use App\Http\Exceptions\{BadRequestException, AuthenticationException, AuthorizationException};

// Set exception handler
set_exception_handler([ExceptionHandler::class, 'handle']);

// Set error handler (convert errors to exceptions)
set_error_handler(function ($severity, $message, $file, $line) {
    if (!(error_reporting() & $severity)) {
        return false;
    }
    throw new ErrorException($message, 0, $severity, $file, $line);
});

// Handle OPTIONS preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Authorization');
    header('Access-Control-Max-Age: 86400');
    http_response_code(200);
    exit;
}

// Session configuration (for hybrid session + JWT auth)
if (!session_id()) {
    ini_set('session.cookie_httponly', '1');
    ini_set('session.cookie_secure', '1');
    ini_set('session.cookie_samesite', 'Strict');
    ini_set('session.gc_maxlifetime', '1800'); // 30 minutes
    session_start();
}

/**
 * Helper: Require specific HTTP method(s)
 *
 * @param array|string $methods Allowed method(s)
 * @throws void Sends 405 response and exits
 */
function require_method($methods): void
{
    $methods = (array) $methods;
    $currentMethod = $_SERVER['REQUEST_METHOD'];

    if (!in_array($currentMethod, $methods, true)) {
        ApiResponse::methodNotAllowed($methods);
    }
}

/**
 * Helper: Read and decode JSON request body
 *
 * @return array Decoded JSON data
 * @throws BadRequestException If JSON is invalid
 */
function read_json_body(): array
{
    $input = file_get_contents('php://input');

    if (empty($input)) {
        return [];
    }

    $data = json_decode($input, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new BadRequestException('Invalid JSON: ' . json_last_error_msg(), 'INVALID_JSON');
    }

    return $data ?? [];
}

/**
 * Helper: Validate required fields
 *
 * @param array $data Input data
 * @param array $required Required field names
 * @throws BadRequestException If required fields missing
 */
function validate_required(array $data, array $required): void
{
    $missing = [];

    foreach ($required as $field) {
        if (!isset($data[$field]) || $data[$field] === '') {
            $missing[] = $field;
        }
    }

    if (!empty($missing)) {
        throw new BadRequestException(
            'Missing required fields: ' . implode(', ', $missing),
            'MISSING_REQUIRED_FIELDS'
        );
    }
}

/**
 * Helper: Get database connection
 *
 * @return PDO Database connection
 */
function get_db(): PDO
{
    static $pdo = null;

    if ($pdo === null) {
        $host = getenv('DB_HOST') ?: 'localhost';
        $dbname = getenv('DB_NAME') ?: 'mydb';
        $user = getenv('DB_USER') ?: 'root';
        $pass = getenv('DB_PASS') ?: '';

        $dsn = "mysql:host={$host};dbname={$dbname};charset=utf8mb4";

        $pdo = new PDO($dsn, $user, $pass, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false
        ]);
    }

    return $pdo;
}

/**
 * Helper: Get Bearer token from Authorization header
 *
 * @return string|null Token or null if not present
 */
function bearer_token(): ?string
{
    $header = $_SERVER['HTTP_AUTHORIZATION'] ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '';

    if (preg_match('/Bearer\s+(.+)/i', $header, $matches)) {
        return $matches[1];
    }

    return null;
}

/**
 * Helper: Require authentication (session or JWT)
 *
 * @return array Auth context (user_id, franchise_id, user_type)
 * @throws AuthenticationException If not authenticated
 */
function require_auth(): array
{
    // Check session first
    if (!empty($_SESSION['user_id'])) {
        // Check session timeout
        $timeout = 1800; // 30 minutes
        if (isset($_SESSION['last_activity']) && (time() - $_SESSION['last_activity']) > $timeout) {
            session_destroy();
            throw new AuthenticationException('Session expired', 'SESSION_EXPIRED');
        }

        $_SESSION['last_activity'] = time();

        return [
            'user_id' => $_SESSION['user_id'],
            'franchise_id' => $_SESSION['franchise_id'] ?? null,
            'user_type' => $_SESSION['user_type'] ?? 'staff'
        ];
    }

    // Check JWT token
    $token = bearer_token();
    if ($token) {
        // Verify JWT (implement your JWT verification here)
        // $payload = JWTService::verify($token);
        // return $payload;

        throw new AuthenticationException('JWT verification not implemented', 'NOT_IMPLEMENTED');
    }

    throw new AuthenticationException('Authentication required', 'UNAUTHORIZED');
}

/**
 * Helper: Require specific permission
 *
 * @param string $permission Permission code
 * @throws AuthorizationException If permission not granted
 */
function require_permission(string $permission): void
{
    $auth = require_auth();

    // Implement permission check here
    // if (!PermissionService::hasPermission($auth['user_id'], $auth['franchise_id'], $permission)) {
    //     throw new AuthorizationException($permission);
    // }

    // For now, super_admin bypasses all
    if (($auth['user_type'] ?? '') === 'super_admin') {
        return;
    }

    // TODO: Implement actual permission checking
    // throw new AuthorizationException($permission);
}

/**
 * Helper: Wrap request handling with try-catch
 *
 * @param callable $handler Request handler function
 */
function handle_request(callable $handler): void
{
    try {
        $handler();
    } catch (Throwable $e) {
        ExceptionHandler::handle($e);
    }
}

/**
 * Helper: Validate CSRF token
 *
 * @throws BadRequestException If CSRF validation fails
 */
function validate_csrf(): void
{
    $token = $_POST['csrf_token'] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';

    if (empty($_SESSION['csrf_token']) || !hash_equals($_SESSION['csrf_token'], $token)) {
        throw new BadRequestException('CSRF validation failed', 'INVALID_CSRF_TOKEN');
    }
}

/**
 * Helper: Generate CSRF token
 *
 * @return string CSRF token
 */
function generate_csrf(): string
{
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }

    return $_SESSION['csrf_token'];
}
