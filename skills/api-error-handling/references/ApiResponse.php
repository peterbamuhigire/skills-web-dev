<?php

namespace App\Http;

/**
 * API Response Helper
 *
 * Standardized response formatting for all API endpoints.
 * Returns JSON with consistent envelope structure.
 */
class ApiResponse
{
    /**
     * Send success response
     *
     * @param mixed $data Response payload
     * @param string $message Optional success message
     * @param int $status HTTP status code (default: 200)
     */
    public static function success($data = null, string $message = '', int $status = 200): void
    {
        self::send([
            'success' => true,
            'data' => $data,
            'message' => $message,
            'meta' => self::getMeta()
        ], $status);
    }

    /**
     * Send created response (201)
     *
     * @param mixed $data Created resource data
     * @param string $message Success message
     */
    public static function created($data = null, string $message = 'Resource created successfully'): void
    {
        self::success($data, $message, 201);
    }

    /**
     * Send error response
     *
     * @param string $message Human-readable error message
     * @param string $code Machine-readable error code
     * @param int $status HTTP status code
     * @param string $type Error type (validation_error, auth_error, etc.)
     * @param array|null $details Additional error details
     */
    public static function error(
        string $message,
        string $code = 'ERROR',
        int $status = 400,
        string $type = 'error',
        ?array $details = null
    ): void {
        $response = [
            'success' => false,
            'message' => $message,
            'error' => [
                'code' => $code,
                'type' => $type
            ],
            'meta' => self::getMeta()
        ];

        if ($details !== null) {
            $response['error']['details'] = $details;
        }

        self::send($response, $status);
    }

    /**
     * Send validation error response (422)
     *
     * @param array $errors Field-specific validation errors
     * @param string $message General error message
     */
    public static function validationError(array $errors, string $message = 'Validation failed'): void
    {
        self::error($message, 'VALIDATION_FAILED', 422, 'validation_error', $errors);
    }

    /**
     * Send not found error (404)
     *
     * @param string $resource Resource type (e.g., "Invoice", "Customer")
     * @param mixed $identifier Resource identifier
     */
    public static function notFound(string $resource, $identifier = null): void
    {
        $message = $identifier
            ? "{$resource} with identifier '{$identifier}' not found"
            : "{$resource} not found";

        self::error($message, strtoupper($resource) . '_NOT_FOUND', 404, 'not_found_error');
    }

    /**
     * Send unauthorized error (401)
     *
     * @param string $message Error message
     */
    public static function unauthorized(string $message = 'Authentication required'): void
    {
        self::error($message, 'UNAUTHORIZED', 401, 'auth_error');
    }

    /**
     * Send forbidden error (403)
     *
     * @param string $permission Required permission
     */
    public static function forbidden(string $permission = ''): void
    {
        $message = $permission
            ? "You do not have permission to perform this action. Required: {$permission}"
            : "You do not have permission to perform this action";

        self::error($message, 'PERMISSION_DENIED', 403, 'authorization_error');
    }

    /**
     * Send conflict error (409)
     *
     * @param string $message Error message
     * @param string $code Error code
     */
    public static function conflict(string $message, string $code = 'CONFLICT'): void
    {
        self::error($message, $code, 409, 'conflict_error');
    }

    /**
     * Send method not allowed error (405)
     *
     * @param array|string $allowedMethods Allowed HTTP methods
     */
    public static function methodNotAllowed($allowedMethods): void
    {
        $methods = is_array($allowedMethods) ? implode(', ', $allowedMethods) : $allowedMethods;

        header("Allow: {$methods}");
        self::error(
            "Method not allowed. Allowed methods: {$methods}",
            'METHOD_NOT_ALLOWED',
            405,
            'method_error'
        );
    }

    /**
     * Send rate limit error (429)
     *
     * @param int $retryAfter Seconds until retry allowed
     */
    public static function rateLimited(int $retryAfter = 60): void
    {
        header("Retry-After: {$retryAfter}");
        self::error(
            "Too many requests. Please try again in {$retryAfter} seconds.",
            'RATE_LIMIT_EXCEEDED',
            429,
            'rate_limit_error'
        );
    }

    /**
     * Send internal server error (500)
     *
     * @param string $message Error message
     */
    public static function serverError(string $message = 'An unexpected error occurred'): void
    {
        self::error($message, 'INTERNAL_ERROR', 500, 'server_error');
    }

    /**
     * Send service unavailable error (503)
     *
     * @param string $message Error message
     */
    public static function serviceUnavailable(string $message = 'Service temporarily unavailable'): void
    {
        self::error($message, 'SERVICE_UNAVAILABLE', 503, 'service_error');
    }

    /**
     * Send JSON response and exit
     *
     * @param array $data Response data
     * @param int $status HTTP status code
     */
    private static function send(array $data, int $status): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');

        // Enable CORS if needed
        if (defined('API_CORS_ENABLED') && API_CORS_ENABLED) {
            header('Access-Control-Allow-Origin: ' . (API_CORS_ORIGIN ?? '*'));
            header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
            header('Access-Control-Allow-Headers: Content-Type, Authorization');
        }

        echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        exit;
    }

    /**
     * Get metadata for response
     *
     * @return array
     */
    private static function getMeta(): array
    {
        return [
            'timestamp' => gmdate('Y-m-d\TH:i:s\Z'),
            'request_id' => self::getRequestId()
        ];
    }

    /**
     * Get or generate request ID
     *
     * @return string
     */
    private static function getRequestId(): string
    {
        static $requestId = null;

        if ($requestId === null) {
            $requestId = $_SERVER['HTTP_X_REQUEST_ID']
                ?? $_SERVER['REQUEST_ID']
                ?? 'req_' . bin2hex(random_bytes(8));
        }

        return $requestId;
    }
}
